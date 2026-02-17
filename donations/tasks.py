import logging
import datetime
from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from donations.models import Donation, Donor, SponsorEmailLog
from donations.services import get_ai_summary
from programs.models.residentials_models import Child

logger = logging.getLogger(__name__)

@shared_task
def send_monthly_donor_emails_task(month=None, year=None, force=False, refresh_ai=False):
    """
    Sends monthly progress emails to donors for their supported children.
    This replaces the previous management command.
    """
    # 1. Determine target month and year (default to previous month)
    today = timezone.now().date()
    first_day_of_current_month = today.replace(day=1)
    last_day_of_prev_month = first_day_of_current_month - datetime.timedelta(days=1)
    
    target_month = month or last_day_of_prev_month.month
    target_year = year or last_day_of_prev_month.year

    logger.info(f"Processing donor reports for {target_month}/{target_year}...")

    # 2. Find donors linked to children via donations
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

            # 3. Get AI Summary
            summary = get_ai_summary(child_obj, target_year, target_month, force_refresh=refresh_ai)
            
            if "No progress records found" in summary:
                logger.warning(f"No progress records for {child_obj.full_name}, skipping.")
                continue
            
            if "An error occurred" in summary:
                raise Exception(f"AI Summary Error: {summary}")

            # 4. Prepare Email
            context = {
                "child_name": child_obj.full_name,
                "child_photo": child_obj.profile_image.url if child_obj.profile_image else None,
                "report_month": datetime.date(2000, target_month, 1).strftime("%B"),
                "report_year": target_year,
                "ai_summary": summary,
                "dashboard_url": getattr(settings, "FRONTEND_URL", "#"),
            }

            html_content = render_to_string("emails/donor_progress_report.html", context)
            text_content = render_to_string("emails/donor_progress_report.txt", context)

            subject = f"Monthly Progress Update: {child_obj.full_name} - {context['report_month']} {target_year}"
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = [donor.email]

            # 5. Send Email
            msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
            msg.attach_alternative(html_content, "text/html")
            msg.send()

            # 6. Log Success
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
            
            # Log Failure if we have enough info
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
