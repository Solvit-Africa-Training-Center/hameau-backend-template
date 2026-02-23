from celery import shared_task

from public_modules.models import ContactMessage
from utils.emails import send_contact_message_email


@shared_task
def send_contact_message_email_task(contact_message_id):
    contact_message = ContactMessage.objects.filter(id=contact_message_id).first()
    if not contact_message:
        return {"sent": False, "reason": "contact_message_not_found"}

    send_contact_message_email(contact_message)
    return {"sent": True}
