from celery import shared_task
from django.apps import apps

@shared_task
def send_status_email_task(application_id):
    InternshipApplication = apps.get_model('programs', 'InternshipApplication')
    try:
        instance = InternshipApplication.objects.get(pk=application_id)
        from utils.emails import send_internship_status_email
        send_internship_status_email(instance)
    except Exception as e:
        print(f"Failed to send email for application {application_id}: {e}")