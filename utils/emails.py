import logging
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.timezone import now

logger = logging.getLogger(__name__)

def send_html_email(subject, template_name, context, recipient_list, from_email=None):
    """
    Generic function to send HTML emails with a text alternative.
    """
    if from_email is None:
        from_email = settings.DEFAULT_FROM_EMAIL
    
    # Render both HTML and Text versions
    html_content = render_to_string(f"{template_name}.html", context)
    try:
        text_content = render_to_string(f"{template_name}.txt", context)
    except:
        # Fallback if text template doesn't exist
        text_content = ""

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=from_email,
        to=recipient_list
    )
    email.attach_alternative(html_content, "text/html")
    
    try:
        return email.send()
    except Exception as e:
        logger.error(f"Failed to send email to {recipient_list}: {str(e)}")
        # We don't want to crash the request if SMTP fails
        return False

def send_internship_status_email(application):
    subject = f"Internship Application Status Update: {application.get_status_display()}"
    context = {
        "application": application,
        "year": now().year,
    }
    return send_html_email(
        subject=subject,
        template_name="emails/internship_status",
        context=context,
        recipient_list=[application.email]
    )


def send_contact_message_notification(message):
    subject = f"New Contact Request: {message.get_reason_display()}"
    context = {
        "fullname": message.fullname,
        "email": message.email,
        "phone": message.phone,
        "reason": message.get_reason_display(),
        "message": message.message,
        "year": now().year,
    }
    
    # We send it to DEFAULT_FROM_EMAIL, assuming that's the main org email.
    # Alternatively, you could add a CONTACT_EMAIL block in settings.
    return send_html_email(
        subject=subject,
        template_name="emails/new_contact_message",
        context=context,
        recipient_list=[settings.DEFAULT_FROM_EMAIL]
    )

