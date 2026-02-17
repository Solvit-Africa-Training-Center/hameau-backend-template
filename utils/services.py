import logging
import uuid
import datetime
import requests
import openai
from django.conf import settings
from django.utils import timezone
from donations.models import ChildMonthlySummary
from programs.models.residentials_models import ChildProgress

logger = logging.getLogger(__name__)

def create_irembopay_invoice(amount, donor_name=None, donor_email=None, donor_phone=None, description="Donation"):
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

def charge_recurring_donation(donation_record):
    """Initiates a secured deduction for a recurring donation via IremboPay Invoice API."""
    donor = donation_record.donor
    amount = donation_record.amount
    
    # Create a new record for this subscription cycle
    irembo_data = create_irembopay_invoice(
        amount=amount,
        donor_name=donor.fullname if donor else "Anonymous",
        donor_email=donor.email if donor else None,
        donor_phone=donor.phone if donor else None,
        description=f"Recurring: {donation_record.donation_purpose}"
    )
    
    if irembo_data:
        invoice_number = irembo_data.get('invoiceNumber')
        payment_link = irembo_data.get('paymentLinkUrl')
        return {
            "success": True, 
            "invoice_number": invoice_number, 
            "payment_link": payment_link
        }
    
    return {"success": False}

def get_ai_summary(child, year, month, force_refresh=False):
    """Generates AI summary of child's progress (cached)."""
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
    if interval == "MONTHLY":
        next_date = start_date + datetime.timedelta(days=31)
        return next_date.replace(day=start_date.day)
    elif interval == "YEARLY":
        try:
            return start_date.replace(year=start_date.year + 1)
        except ValueError:
            # Handle leap year Feb 29
            return start_date + datetime.timedelta(days=365)
    return None
