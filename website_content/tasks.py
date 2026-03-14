from celery import shared_task
from utils.emails import send_html_email
from django.conf import settings


@shared_task
def send_contact_message_email(contact_message, email):
    send_html_email(
        subject="New Contact Message",
        template_name="emails/contact_message",
        context={
            "message": contact_message,
        },
        recipient_list=[email],
    )
