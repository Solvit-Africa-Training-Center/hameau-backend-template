import logging
import datetime
from celery import shared_task
from django.conf import settings
from django.utils import timezone
from donations.models import Donation, Donor, SponsorEmailLog
from programs.models.residentials_models import Child
from utils.emails import send_html_email
from utils.services import (
    get_ai_summary, 
    calculate_next_deduction_date, 
    charge_recurring_donation
)

logger = logging.getLogger(__name__)


@shared_task
def send_monthly_donor_emails_task(month=None, year=None, force=False, refresh_ai=False):
    """Automated task to send monthly progress reports to donors."""
    # Target month and year (default to previous month)
    today = timezone.now().date()
    first_day_of_current_month = today.replace(day=1)
    last_day_of_prev_month = first_day_of_current_month - datetime.timedelta(days=1)
    
    target_month = month or last_day_of_prev_month.month
    target_year = year or last_day_of_prev_month.year

    logger.info(f"Processing donor reports for {target_month}/{target_year}...")

    # Find donors linked to children
    active_donor_child_pairs = Donation.objects.filter(
        child__isnull=False,
        donor__isnull=False
    ).values('donor', 'child').distinct()

    total_sent = 0
    total_errors = 0

    for pair in active_donor_child_pairs:
        try:
            donor = Donor.objects.get(id=pair['donor'])
            child_obj = Child.objects.get(id=pair['child'])

            if not donor.email:
                logger.warning(f"Donor {donor.fullname} has no email, skipping.")
                continue

            # Check if already sent
            if not force:
                if SponsorEmailLog.objects.filter(
                    donor=donor,
                    child=child_obj,
                    month=target_month,
                    year=target_year,
                    status="SUCCESS"
                ).exists():
                    logger.info(f"Skipping {donor.fullname} for {child_obj.full_name} (Already sent)")
                    continue

            # Get AI Summary
            summary = get_ai_summary(child_obj, target_year, target_month, force_refresh=refresh_ai)
            
            if "No progress records found" in summary:
                logger.warning(f"No progress records for {child_obj.full_name}, skipping.")
                continue
            
            if "An error occurred" in summary:
                raise Exception(f"AI Summary Error: {summary}")

            # Prepare Context
            context = {
                "child_name": child_obj.full_name,
                "child_photo": child_obj.profile_image.url if child_obj.profile_image else None,
                "report_month": datetime.date(2000, target_month, 1).strftime("%B"),
                "report_year": target_year,
                "ai_summary": summary,
                "dashboard_url": getattr(settings, "FRONTEND_URL", "#"),
            }

            subject = f"Monthly Progress Update: {child_obj.full_name} - {context['report_month']} {target_year}"
            from_email = settings.DEFAULT_FROM_EMAIL
            to_emails = [donor.email]

            # Send Email
            send_html_email(
                subject=subject,
                template_name="emails/donor_progress_report",
                context=context,
                recipient_list=to_emails,
                from_email=from_email
            )

            # Log Success
            SponsorEmailLog.objects.create(
                donor=donor,
                child=child_obj,
                month=target_month,
                year=target_year,
                status="SUCCESS"
            )
            
            total_sent += 1
            logger.info(f"Successfully sent email to {donor.email} for {child_obj.full_name}")

        except Exception as e:
            total_errors += 1
            error_msg = str(e)
            logger.error(f"Failed to send email to {pair['donor']} for child {pair['child']}: {error_msg}")
            
            # Log Failure for visibility in the database
            try:
                donor = Donor.objects.get(id=pair['donor'])
                child_obj = Child.objects.get(id=pair['child'])
                SponsorEmailLog.objects.create(
                    donor=donor,
                    child=child_obj,
                    month=target_month,
                    year=target_year,
                    status="FAILED",
                    error_message=error_msg
                )
            except Exception as inner_e:
                logger.error(f"Critical error while logging failure: {inner_e}")

    logger.info(f"Completed. Sent: {total_sent}, Errors: {total_errors}")
    return {"sent": total_sent, "errors": total_errors}

@shared_task
def process_recurring_donations_task():
    """Daily task to process automatic deductions for recurring donations."""
    today = timezone.now().date()
    due_recurring = Donation.objects.filter(
        is_recurring=True,
        next_deduction_date__lte=today
    )

    processed_count = 0
    error_count = 0

    for subscription_record in due_recurring:
        try:
            # Initiate Secured Deduction
            result = charge_recurring_donation(subscription_record)
            
            if result.get("success"):
                # Create new Donation record
                notes = f"Automatic recurring payment processed. Invoice: {result.get('invoice_number')}"
                if result.get('payment_link'):
                    notes += f"\nPayment Link: {result.get('payment_link')}"
                
                new_donation = Donation.objects.create(
                    donor=subscription_record.donor,
                    donation_type=subscription_record.donation_type,
                    child=subscription_record.child,
                    family=subscription_record.family,
                    amount=subscription_record.amount,
                    currency=subscription_record.currency,
                    donation_purpose=subscription_record.donation_purpose,
                    payment_method=subscription_record.payment_method,
                    is_recurring=True, # This new record becomes the active subscription record
                    recurring_interval=subscription_record.recurring_interval,
                    notes=f"{notes}\n\nProcessed from subscription {subscription_record.id}"
                )
                
                # Calculate next deduction date
                new_next_date = calculate_next_deduction_date(
                    new_donation.donation_date.date(), 
                    new_donation.recurring_interval
                )
                new_donation.next_deduction_date = new_next_date
                new_donation.save()

                # Mark old record as processed
                subscription_record.is_recurring = False
                subscription_record.save()
                
                processed_count += 1
                logger.info(f"Successfully processed recurring donation {new_donation.id} for {subscription_record.donor.fullname}")
            else:
                logger.error(f"Failed to process secured deduction for donation {subscription_record.id}")
                error_count += 1

        except Exception as e:
            error_count += 1
            logger.error(f"Error processing recurring donation {subscription_record.id}: {e}")

    return {"processed": processed_count, "errors": error_count}
