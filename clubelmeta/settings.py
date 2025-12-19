from pathlib import Path
import os
from dotenv import load_dotenv
import dj_database_url
import cloudinary

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


# ---------------------------
# SECURITY
# ---------------------------
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
DEBUG = False


# ---------------------------
# ALLOWED HOSTS
# ---------------------------
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")

if DEBUG:
    ALLOWED_HOSTS += ["127.0.0.1", "localhost"]

ALLOWED_HOSTS = [h.strip() for h in ALLOWED_HOSTS if h.strip()]


# ---------------------------
# CSRF CONFIG (Railway / Dominio)
# ---------------------------
CSRF_TRUSTED_ORIGINS = [
    "https://*.railway.app",
    "https://clubelmeta-production.up.railway.app",
]


# ---------------------------
# APPS
# ---------------------------
INSTALLED_APPS = [
    # Cloudinary
    "cloudinary",
    "cloudinary_storage",

    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",

    # Local
    "reservas.apps.ReservasConfig",
]


# ---------------------------
# EMAIL CONFIG
# ---------------------------
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

EMAIL_HOST = os.getenv("EMAIL_HOST", "")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True") == "True"

EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")

DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", EMAIL_HOST_USER)
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", EMAIL_HOST_USER)


# ---------------------------
# MIDDLEWARE
# ---------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]



# ---------------------------
# URLS Y WSGI
# ---------------------------
ROOT_URLCONF = "clubelmeta.urls"
WSGI_APPLICATION = "clubelmeta.wsgi.application"


# ---------------------------
# TEMPLATES
# ---------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.template.context_processors.csrf",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# ---------------------------
# DATABASE
# ---------------------------
# Producción: PostgreSQL (Railway)
# Local: SQLite automático
DATABASES = {
    "default": dj_database_url.config(
        default="sqlite:///db.sqlite3",
        conn_max_age=600,
        ssl_require=not DEBUG,
    )
}


# ---------------------------
# PASSWORD VALIDATION
# ---------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# ---------------------------
# INTERNATIONALIZATION
# ---------------------------
LANGUAGE_CODE = "es"
TIME_ZONE = "America/Bogota"

USE_I18N = True
USE_L10N = True
USE_TZ = True

LOCALE_PATHS = [BASE_DIR / "locale"]

from django.utils.translation import gettext_lazy as _

LANGUAGES = [
    ("es", _("Spanish")),
]


STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# ---------------------------
# MEDIA FILES (Cloudinary)
# ---------------------------
DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"
MEDIA_URL = "/media/"


cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True,
)


# ---------------------------
# LOGIN CONFIG
# ---------------------------
LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/panel/"
LOGOUT_REDIRECT_URL = "/"


# ---------------------------
# DEFAULT AUTO FIELD
# ---------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
