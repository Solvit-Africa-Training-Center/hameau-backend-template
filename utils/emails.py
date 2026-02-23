from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.timezone import now

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
    return email.send()

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


def send_contact_message_email(contact_message):
    subject = f"New Website Contact Inquiry: {contact_message.name}"
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient = getattr(settings, "CONTACT_RECIPIENT_EMAIL", settings.DEFAULT_FROM_EMAIL)

    text_content = (
        "A new contact inquiry was submitted through the website contact form.\n\n"
        f"Name: {contact_message.name}\n"
        f"Email: {contact_message.email}\n"
        f"Phone Number: {contact_message.phone_number}\n\n"
        "Message:\n"
        f"{contact_message.message}\n\n"
        f"Submitted On: {contact_message.created_on}\n"
    )

    html_content = f"""
    <h3>New Contact Inquiry</h3>
    <p>A new contact inquiry was submitted through the website contact form.</p>
    <p><strong>Name:</strong> {contact_message.name}</p>
    <p><strong>Email:</strong> {contact_message.email}</p>
    <p><strong>Phone Number:</strong> {contact_message.phone_number}</p>
    <p><strong>Message:</strong></p>
    <p>{contact_message.message}</p>
    <p><strong>Submitted On:</strong> {contact_message.created_on}</p>
    """

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=from_email,
        to=[recipient],
        reply_to=[contact_message.email],
    )
    email.attach_alternative(html_content, "text/html")
    return email.send()

