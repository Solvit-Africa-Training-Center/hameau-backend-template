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

