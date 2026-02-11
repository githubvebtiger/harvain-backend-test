from .local import *

# CORS configuration
MIDDLEWARE.insert(
    MIDDLEWARE.index("django.middleware.common.CommonMiddleware") - 1,
    "corsheaders.middleware.CorsMiddleware",
)

# SECURITY: Only allow specific origins, not all
# DANGEROUS: Never set CORS_ALLOW_ALL_ORIGINS = True with CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_CREDENTIALS = True

# Exact origins for local development
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "http://app.harvain.local:3000",
    "http://app.harvain.local:3001",
]

# Regex patterns for production domains (supports subdomains)
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https?://([a-zA-Z0-9-]+\.)?gramline\.com$",  # *.gramline.com and gramline.com
    r"^https?://([a-zA-Z0-9-]+\.)?greekz\.com$",    # *.greekz.com and greekz.com
    r"^https?://([a-zA-Z0-9-]+\.)?neosona\.com$",   # *.neosona.com and neosona.com
    r"^https?://([a-zA-Z0-9-]+\.)?bttrades\.com$",  # *.bttrades.com and bttrades.com
    r"^https?://([a-zA-Z0-9-]+\.)?harvain\.com$",   # *.harvain.com and harvain.com
]

# CSRF trusted origins (supports wildcards)
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "http://app.harvain.local:3000",
    "http://app.harvain.local:3001",
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

# For local development only - should be restricted in production
ALLOWED_HOSTS = ["*"]  # TODO: Restrict in production settings
