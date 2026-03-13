from django.db.models.signals import post_save
from django.dispatch import receiver
from website_content.models import ContactMessage, ReplyToContactMessage
from website_content.tasks import send_contact_message_email
from django.conf import settings


@receiver(post_save, sender=ContactMessage)
def create_contact_message(sender, instance, created, **kwargs):
    if created:
        send_contact_message_email(instance.id, settings.EMAIL_CONTACT)


@receiver(post_save, sender=ReplyToContactMessage)
def create_reply_to_contact_message(sender, instance, created, **kwargs):
    if created:
        send_contact_message_email(instance.id, instance.contact_message.email)
