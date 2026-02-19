from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.timezone import now

def send_internship_status_email(application):
    subject = f"Internship Application Status Update: {application.get_status_display()}"

    context = {
        "application": application,
        "year": now().year,
    }

    html_content = render_to_string("emails/internship_status.html", context)
    text_content = f"Hello {application.first_name},\n\nYour internship application status has been updated to: {application.get_status_display()}.\n\nLog in to your portal for more details."

    email_message = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[application.email],
    )

    email_message.attach_alternative(html_content, "text/html")
    return email_message.send()

def send_contact_message_email(instance):
    
    #Sends an email notification when a new contact message is received.
    
    subject = f"New Contact Message: {instance.subject}"
    
    context = {
        "instance": instance,
        "year": now().year,
    }

    html_content = render_to_string("emails/contact_message.html", context)
    text_content = f"""
    New Contact Message
    
    From: {instance.first_name} {instance.last_name}
    Email: {instance.email}
    Phone: {instance.phone}
    
    Subject: {instance.subject}
    
    Message:
    {instance.message}
    """

    email_message = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL, # Sender
        to=[settings.DEFAULT_FROM_EMAIL],       # Receiver (Admin)
        reply_to=[instance.email],              # Allow replying to the sender
    )

    email_message.attach_alternative(html_content, "text/html")
    return email_message.send()