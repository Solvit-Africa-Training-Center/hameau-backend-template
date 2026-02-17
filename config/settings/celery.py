from . base import env
from celery.schedules import crontab

CELERY_BROKER_URL=env("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND=env("CELERY_RESULT_BACKEND")

CELERY_BROKER_USE_SSL = {
    'ssl_cert_reqs': 'none'
}
CELERY_REDIS_BACKEND_USE_SSL = {
    'ssl_cert_reqs': 'none'
}

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC' 

CELERY_BEAT_SCHEDULE = {
    "send-monthly-donor-reports": {
        "task": "donations.tasks.send_monthly_donor_emails_task",
        "schedule": crontab(day_of_month=1, hour=0, minute=0),
    },
    "process-recurring-donations": {
        "task": "donations.tasks.process_recurring_donations_task",
        "schedule": crontab(hour=0, minute=0),
    },
}
