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

