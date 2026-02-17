import logging
import datetime
import uuid
import openai
import requests
from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from donations.models import Donation, Donor, SponsorEmailLog, ChildMonthlySummary
from programs.models.residentials_models import Child, ChildProgress

logger = logging.getLogger(__name__)

def create_irembopay_invoice(amount, donor_name=None, donor_email=None, donor_phone=None, description="Donation"):
    """
    Creates an invoice on IremboPay and returns the response data.
    """
    url = f"{settings.IREMBOPAY_BASE_URL}/payments/invoices"
    headers = {
        "Content-Type": "application/json",
        "irembopay-secretKey": settings.IREMBOPAY_SECRET_KEY,
        "X-API-Version": settings.IREMBOPAY_API_VERSION
    }
    
    transaction_id = f"DON-{uuid.uuid4().hex[:10].upper()}"
    
    payload = {
        "transactionId": transaction_id,
        "paymentAccountIdentifier": settings.IREMBOPAY_ACCOUNT_ID,
        "paymentItems": [
            {
                "code": "DONATION",
                "quantity": 1,
                "unitAmount": float(amount)
            }
        ],
        "description": description,
        "language": "EN"
    }
    
    if donor_name or donor_email or donor_phone:
        payload["customer"] = {}
        if donor_name:
            payload["customer"]["name"] = donor_name
        if donor_email:
            payload["customer"]["email"] = donor_email
        if donor_phone:
            try:
                payload["customer"]["phoneNumber"] = int(''.join(filter(str.isdigit, donor_phone)))
            except (ValueError, TypeError):
                pass

    try:
        logger.info(f"Initiating IremboPay invoice for {transaction_id}, amount: {amount}")
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        if data.get("success"):
            logger.info(f"Successfully created IremboPay invoice: {data['data']['invoiceNumber']}")
            return data["data"]
        else:
            logger.error(f"IremboPay API returned success=False: {data}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error calling IremboPay API: {e}")
        return None

def get_ai_summary(child, year, month, force_refresh=False):
    """
    Generates a natural language summary of a child's progress for a given month using OpenAI.
    Caches the results in ChildMonthlySummary to avoid redundant API calls.
    """
    if not force_refresh:
        cached = ChildMonthlySummary.objects.filter(
            child=child, month=month, year=year
        ).first()
        if cached:
            return cached.summary_text

    try:
        progress_records = ChildProgress.objects.filter(
            child=child,
            created_on__year=year,
            created_on__month=month
        ).prefetch_related('progress_media')

        if not progress_records.exists():
            return f"No progress records found for {child.first_name} in {month}/{year}."

        notes_list = []
        total_images = 0
        total_videos = 0

        for record in progress_records:
            date_str = record.created_on.strftime("%d %b")
            notes_list.append(f"- {date_str}: {record.notes}")
            
            media_items = record.progress_media.all()
            for media in media_items:
                if media.progress_image:
                    total_images += 1
                if media.progress_video:
                    total_videos += 1

        formatted_notes = "\n".join(notes_list)

        prompt = (
            f"Write a short, warm, and encouraging summary of the child's progress based on the following monthly updates. "
            f"The child's name is {child.first_name}. "
            f"The period is {month}/{year}. "
            f"Mention key activities and improvements. "
            f"Mention that there are {total_images} photos and {total_videos} videos attached if the counts are greater than zero. "
            f"Keep the tone positive and suitable for a sponsor report.\n\n"
            f"Updates:\n{formatted_notes}"
        )

        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", 
            messages=[
                {"role": "system", "content": "You are a helpful assistant writing progress summaries for child sponsorship reports."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.7,
        )

        summary = response.choices[0].message.content.strip()

        ChildMonthlySummary.objects.update_or_create(
            child=child,
            month=month,
            year=year,
            defaults={"summary_text": summary}
        )

        return summary

    except Exception as e:
        logger.error(f"Error generating AI summary for child {child.id}: {e}")
        return "An error occurred while generating the summary. Please check the logs."

def calculate_next_deduction_date(start_date, interval):
    """
    Calculates the next deduction date based on the interval.
    """
    if interval == "MONTHLY":
        # Add a month
        next_date = start_date + datetime.timedelta(days=31)
        return next_date.replace(day=start_date.day)
    elif interval == "YEARLY":
        # Add a year
        try:
            return start_date.replace(year=start_date.year + 1)
        except ValueError:
            # Handle leap year Feb 29
            return start_date + datetime.timedelta(days=365)
    return None


@shared_task
def send_monthly_donor_emails_task(month=None, year=None, force=False, refresh_ai=False):
    """
    Automated task to send monthly progress reports to donors.
    
    Logic:
    1. Identifies active donor-child pairs based on donations.
    2. Fetches an AI-generated summary of the child's progress for the specified month.
    3. Renders HTML and plain-text email templates.
    4. Sends the email and logs the result in SponsorEmailLog.
    
    Args:
        month (int): Optional. Target month (1-12). Defaults to previous month.
        year (int): Optional. Target year. Defaults to previous month's year.
        force (bool): If True, resends even if a successful log exists for the donor/child/month.
        refresh_ai (bool): If True, forces OpenAI to regenerate the summary.
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

            # 3. Get AI Summary from service layer
            summary = get_ai_summary(child_obj, target_year, target_month, force_refresh=refresh_ai)
            
            if "No progress records found" in summary:
                logger.warning(f"No progress records for {child_obj.full_name}, skipping.")
                continue
            
            if "An error occurred" in summary:
                raise Exception(f"AI Summary Error: {summary}")

            # 4. Prepare Email Context
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

            # 5. Send Email using Utility from utils.emails
            from utils.emails import send_html_email
            send_html_email(
                subject=subject,
                template_name="emails/donor_progress_report",
                context=context,
                recipient_list=to_emails,
                from_email=from_email
            )

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
    """
    Background task to process automatic secured deductions for recurring donations.
    Runs daily to identify donations whose next_deduction_date has arrived.
    """
    today = timezone.now().date()
    due_recurring = Donation.objects.filter(
        is_recurring=True,
        next_deduction_date__lte=today
    )

    processed_count = 0
    error_count = 0

    for subscription_record in due_recurring:
        try:
            # 1. Initiate "Secured Deduction" via Payment Gateway (Placeholder)
            # In a real scenario, we'd use the stored payment token/method to charge the donor.
            # success = irembo_service.charge_recurring(subscription_record)
            success = True # Simulating success for now
            
            if success:
                from .services import calculate_next_deduction_date
                
                # 2. Create the new Donation record for the current payment
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
                    notes=f"Automatic recurring payment processed from subscription {subscription_record.id}"
                )
                
                # 3. Calculate and set the next deduction date for the NEW record
                new_next_date = calculate_next_deduction_date(
                    new_donation.donation_date.date(), 
                    new_donation.recurring_interval
                )
                new_donation.next_deduction_date = new_next_date
                new_donation.save()

                # 4. Mark the old record as no longer "the active recurring template"
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
