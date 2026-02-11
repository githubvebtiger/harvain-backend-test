import os

# region				-----External Imports-----
from django.core.management.utils import get_random_secret_key

# region				-----Internal Imports-----
from .django import *
from .project import *
from .third_party import *

# endregion

# endregion

SECRET_KEY = os.environ.get("SECRET_KEY", get_random_secret_key())

DEBUG = False

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1,bttrades.com,www.bttrades.com").split(",")

DATABASES = {
    "default": {
        "PASSWORD": os.environ.get("DATABASE_PASSWORD"),
        "HOST": os.environ.get("DATABASE_HOST"),
        "NAME": os.environ.get("DATABASE_NAME"),
        "PORT": os.environ.get("DATABASE_PORT"),
        "USER": os.environ.get("DATABASE_USER"),
        "ENGINE": os.environ.get("ENGINE"),
        "ATOMIC_REQUESTS": True,
    }
}

# SASS

COMPRESS_OFFLINE = True
LIBSASS_OUTPUT_STYLE = "compressed"
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"

# CACHE

# CACHES = {
#     'default': {
#         'BACKEND': 'django_redis.cache.RedisCache',
#         'LOCATION': f'redis://{os.environ.get("REDIS_HOST","127.0.0.1")}:{os.environ.get("REDIS_PORT",6379)}/1',
#     }
# }

# MIDDLEWARE = ['django.middleware.cache.UpdateCacheMiddleware'] + \
#              MIDDLEWARE + \
#              ['django.middleware.cache.FetchFromCacheMiddleware']

MIDDLEWARE = (
    ["django.middleware.cache.UpdateCacheMiddleware"]
    + MIDDLEWARE
    + [
        "django.middleware.cache.FetchFromCacheMiddleware",
        "utils.first_party.middleware.Process500Error",
    ]
)

# CORS
INSTALLED_APPS += ["corsheaders"]

MIDDLEWARE.insert(
    MIDDLEWARE.index("django.middleware.common.CommonMiddleware") - 1,
    "corsheaders.middleware.CorsMiddleware",
)

# CORS configuration - supports all production domains
CORS_ALLOW_CREDENTIALS = True

# Exact origins for local development and env-based frontend
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Add FRONTEND_DOMAIN from environment if set
if os.environ.get("FRONTEND_DOMAIN"):
    CORS_ALLOWED_ORIGINS.extend([
        f'http://{os.environ.get("FRONTEND_DOMAIN")}',
        f'https://{os.environ.get("FRONTEND_DOMAIN")}',
    ])

# Regex patterns for all production domains (supports subdomains)
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https?://([a-zA-Z0-9-]+\.)?gramline\.com$",
    r"^https?://([a-zA-Z0-9-]+\.)?greekz\.com$",
    r"^https?://([a-zA-Z0-9-]+\.)?neosona\.com$",
    r"^https?://([a-zA-Z0-9-]+\.)?bttrades\.com$",
    r"^https?://([a-zA-Z0-9-]+\.)?harvain\.com$",
]

# CSRF trusted origins
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://*.gramline.com",
    "http://*.gramline.com",
    "https://*.greekz.com",
    "http://*.greekz.com",
    "https://*.neosona.com",
    "http://*.neosona.com",
    "https://*.bttrades.com",
    "http://*.bttrades.com",
    "https://*.harvain.com",
    "http://*.harvain.com",
]

# Allow common headers
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

print(">>> START PROJECT WITH PROD SETTINGS <<<")
