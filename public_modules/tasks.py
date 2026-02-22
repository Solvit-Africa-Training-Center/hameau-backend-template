from celery import shared_task
from public_modules.models.content_models import ContactMessage
from utils.emails import send_contact_message_email

@shared_task
def send_contact_message_email_task(contact_message_id):
    try:
        instance = ContactMessage.objects.get(id=contact_message_id)
        send_contact_message_email(instance)
    except ContactMessage.DoesNotExist:
        pass
