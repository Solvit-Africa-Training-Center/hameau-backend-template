from .base import env
from .base import BASE_DIR

# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.postgresql",
#         "NAME": env("Hamau_de_jeune_program_db"),
#         "USER": env("postgres"),
#         "PASSWORD": env("admin"),
#         "HOST": env("localhost"),
#         "PORT": env("5432"),
#         "OPTIONS": {"sslmode": "require"},
#     }
# }

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "dbc.sqlite3",
    }
}
