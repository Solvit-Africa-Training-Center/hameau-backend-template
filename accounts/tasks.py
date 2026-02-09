from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.timezone import now
from celery import shared_task

@shared_task
def send_temporary_credentials_task(email, password):
    subject = "Account created at Hameau des Jeunes"

    context = {
        "password": password,
        "email": email,
        "year": now().year,
    }

    html_content = render_to_string("emails/email_temporary_credentials.html", context)
    text_content = f"Your temporary credentials are\n\n -Email: {email} \n -Password: {password}.\nUse these credentials to login after you verify your email (You have received or you'll soon receive an email containing the code)"

    email_message = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[email],
    )

    email_message.attach_alternative(html_content, "text/html")
    return email_message.send()

@shared_task
def send_password_reset_email_task(email, code):
    subject = "Reset your password"

    context = {
        "code": code,
        "year": now().year,
    }

    html_content = render_to_string("emails/email_reset_password.html", context)
    text_content = f"Your password reset code is: {code}"

    email_message = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[email],
    )

    email_message.attach_alternative(html_content, "text/html")
    return email_message.send()