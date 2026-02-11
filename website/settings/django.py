import os
import sys
import logging
from pathlib import Path

# region				-----External Imports-----
# Google Cloud Translation - imported conditionally to avoid crashes if credentials missing
try:
    from google.cloud import translate
    GOOGLE_TRANSLATE_AVAILABLE = True
except Exception as e:
    logging.warning(f"Google Cloud Translation import failed: {e}")
    GOOGLE_TRANSLATE_AVAILABLE = False

# endregion

# region			  -----Supporting Variables-----
BASE_DIR = Path(__file__).resolve().parent.parent.parent
FRONTEND_DOMAIN = os.environ.get("FRONTEND_DOMAIN")
# endregion

# region		     -----Application Definition-----
THIRD_PARTY_APPS = [
    "modeltranslation",
    "drf_spectacular",
    "django_filters",
    "rest_framework",
    "compressor",
    "jazzmin",
    "django_celery_beat",
]


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
]

USER_APPS = ["football", "user", "geo", "finance", "bets", "history", "news"]

INSTALLED_APPS = THIRD_PARTY_APPS + INSTALLED_APPS + USER_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "website.middleware.SaveIPMiddleware",
    "history.middleware.CurrentUserMiddleware",
]

LOCALE_PATHS = (os.path.join(BASE_DIR, "locale"),)

ROOT_URLCONF = "website.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(BASE_DIR, "templates"),
        ],
        "OPTIONS": {
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.template.context_processors.media",
                "django.template.context_processors.csrf",
                "django.template.context_processors.tz",
                "django.template.context_processors.static",
            ],
            "loaders": [
                "django.template.loaders.filesystem.Loader",
                "django.template.loaders.app_directories.Loader",
            ],
        },
    },
]

WSGI_APPLICATION = "website.wsgi.application"

SITE_ID = 1

AUTH_USER_MODEL = "user.User"

SITE_ID = 1
# endregion

# region			  -----Password Validations-----
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 8,
        },
    },
    {
        "NAME": "user.validators.MaximumLengthValidator",
        "OPTIONS": {
            "max_length": 20,
        },
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
    {
        "NAME": "user.validators.UppercaseValidator",
    },
    {
        "NAME": "user.validators.LatinCharacterValidator",
    },
]
# endregion

# region			  -----Internationalization-----
TIME_ZONE = "Europe/Moscow"

USE_I18N = True
USE_SSL = False
USE_TZ = True

DATE_INPUT_FORMATS = ("%d.%m.%Y", "%Y-%m-%d")

LOGIN_URL = "/?login=true"
LOGOUT_REDIRECT_URL = "/"
# endregion

# region				  -----Static files-----
STATIC_URL = "/static/"
ADMIN_MEDIA_PREFIX = "/static/admin/"

STATIC_ROOT = os.path.join(BASE_DIR, "allstaticfiles")

STATICFILE_DIR = os.path.join(BASE_DIR, "allstaticfiles/static")
STATICFILES_DIRS = (STATICFILE_DIR, os.path.join(BASE_DIR, "website/static"))
STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "compressor.finders.CompressorFinder",
)

TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
# endregion

# region				     -----Fields-----
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
# endregion

# region				     -----Medias-----
MEDIA_FOLDER = "media"
MEDIA_ROOT = os.path.join(BASE_DIR, MEDIA_FOLDER)
MEDIA_URL = "/media/"
# endregion

# region				    -----Loggings-----
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
        },
        "mail_admins": {
            "level": "ERROR",
            "class": "django.utils.log.AdminEmailHandler",
            "include_html": True,
        },
        "errors_log": {
            "level": "ERROR",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(BASE_DIR, "errors.log"),
            "maxBytes": 1024 * 1024 * 10,
            "backupCount": 7,
            "formatter": "verbose",
        },
    },
    "loggers": {
        "": {
            "level": "INFO",
            "handlers": ["console"],
        },
        "django.request": {
            "handlers": ["mail_admins", "errors_log", "console"],
            "level": "DEBUG",
            "propagate": False,
        },
        # 'django.db.backends': {
        #     'level': 'DEBUG',
        #     'handlers': ['console'],
        # }
    },
}

# Google Cloud Translation Client - graceful degradation if credentials missing
if GOOGLE_TRANSLATE_AVAILABLE:
    try:
        google_cloud_client = translate.TranslationServiceClient()
        logging.info("Google Cloud Translation client initialized successfully")
    except Exception as e:
        logging.warning(f"Failed to initialize Google Translation client: {e}")
        logging.warning("Google Translation features will be disabled")
        google_cloud_client = None
else:
    logging.warning("Google Cloud Translation not available - features will be disabled")
    google_cloud_client = None
# endregion
