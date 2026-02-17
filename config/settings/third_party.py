from .base import env
import cloudinary
import os

CLOUDINARY_STORAGE = {
    "CLOUD_NAME": os.environ.get("CLOUDINARY_CLOUD_NAME"),
    "API_KEY": os.environ.get("CLOUDINARY_API_KEY"),
    "API_SECRET": os.environ.get("CLOUDINARY_API_SECRET"),
}
cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
    api_key=os.environ.get("CLOUDINARY_API_KEY"),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET"),
)

OPENAI_API_KEY = env("OPENAI_API_KEY", default="")

STORAGES = {
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

IREMBOPAY_SECRET_KEY = env("IREMBOPAY_SECRET_KEY", default="secreKey")
IREMBOPAY_BASE_URL = env("IREMBOPAY_BASE_URL", default="https://api.sandbox.irembopay.com")
IREMBOPAY_ACCOUNT_ID = env("IREMBOPAY_ACCOUNT_ID", default="TST-RWF")
IREMBOPAY_API_VERSION = env("IREMBOPAY_API_VERSION", default="3")