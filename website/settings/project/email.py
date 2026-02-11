import os
from dotenv import load_dotenv

load_dotenv()

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 465
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
EMAIL_USE_SSL = True
FRONTEND_DOMAIN = os.environ.get('FRONTEND_DOMAIN')
BACK_DOMAIN = os.environ.get('BACK_DOMAIN')
