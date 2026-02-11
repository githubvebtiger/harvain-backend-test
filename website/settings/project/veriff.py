import os
from dotenv import load_dotenv

load_dotenv()

# Veriff API configuration
VERIFF_BASE_URL = os.environ.get('VERIFF_BASE_URL')
VERIFF_API_KEY = os.environ.get('VERIFF_API_KEY')

# IMPORTANT: Webhook signature verification
# Set this to enable secure webhook signature verification
# Get this from Veriff dashboard: https://station.veriff.com/
# If not set, webhook will work WITHOUT signature verification (less secure)
SHARED_SECRET = os.environ.get('VERIFF_SHARED_SECRET')
