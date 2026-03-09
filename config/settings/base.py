from pathlib import Path
import environ 
import os
from datetime import timedelta, date
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent.parent


env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG", cast=bool)
ALLOWED_HOSTS = env("ALLOWED_HOSTS").split(",")

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework.authtoken',
    'drf_spectacular',
    'corsheaders',
    "rest_framework_simplejwt.token_blacklist",
    "django_filters",

    'django.contrib.sites',
   

    'cloudinary',
    'cloudinary_storage',

    'accounts',
    'public_modules',
    'programs',
    'donations',
    'website_content',
]

SITE_ID = 1

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware', 
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

APPEND_SLASH = True

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

VERIFICATION_CODE_LIFETIME = timedelta(minutes=15)

start_since_raw = env("START_SINCE", default="").strip()
if not start_since_raw:
    raise ImproperlyConfigured(
        "START_SINCE must be set in environment as a valid date (YYYY-MM-DD)."
    )
try:
    START_SINCE = date.fromisoformat(start_since_raw)
except ValueError as exc:
    raise ImproperlyConfigured(
        "START_SINCE must be a valid date in YYYY-MM-DD format."
    ) from exc


