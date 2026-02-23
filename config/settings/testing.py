from .dev import *

# Test-specific overrides
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

CELERY_TASK_ALWAYS_EAGER = True
CELERY_BROKER_URL = 'memory://'
CELERY_RESULT_BACKEND = 'cache+memory://'
CELERY_BROKER_USE_SSL = None
CELERY_REDIS_BACKEND_USE_SSL = None

STORAGES = { 
    'default': { 'BACKEND': 'django.core.files.storage.FileSystemStorage' }, 
    'staticfiles': { 'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage' } 
}
