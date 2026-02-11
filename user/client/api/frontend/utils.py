import requests
from typing import Union

from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string

from ....models import Client
from ....satellite.models import Satellite


def send_email_message_verification(user: Client, activate_url: str) -> None:
    subject = "Confirm your email"
    html_message = f"""
    <html>
      <body>
        <p>Hello, <strong>{user.username}</strong>!</p>
        <p>To confirm your email, please follow the link below:</p>
        <p><a href="{activate_url}">Confirm Email</a></p>
        <p>If the button doesn't work, copy and paste this link into your browser:</p>
        <p>{activate_url}</p>
        <p>Thank you for being with us!</p>
      </body>
    </html>
    """

    message = EmailMultiAlternatives(
        subject=subject,
        body="",
        from_email=settings.EMAIL_HOST_USER,
        to=[user.email],
    )
    message.attach_alternative(html_message, "text/html")
    message.send()


def get_frontend_base_url(request) -> str:
    """
    Extract frontend base URL from request.
    Uses Origin or Referer header, or falls back to default.
    Always returns HTTPS URL (required by Veriff).
    """
    # Try Origin header first (set by browser for CORS requests)
    origin = request.headers.get('Origin')
    if origin:
        # Force HTTPS for Veriff callback requirement
        return origin.replace('http://', 'https://')

    # Try Referer header
    referer = request.headers.get('Referer')
    if referer:
        from urllib.parse import urlparse
        parsed = urlparse(referer)
        return f"https://{parsed.netloc}"

    # Fallback to default
    return "https://harvain.com"


def create_veriff_session(user: Union[Client, Satellite], lang: str = "en", request=None) -> str:
    # Get frontend base URL from request
    if request:
        base_url = get_frontend_base_url(request)
    else:
        base_url = "https://harvain.com"

    callback_url = f"{base_url}/verification-done"

    payload = {
        "verification": {
            "callback": callback_url,
            "person": {
                "firstName": user.name,
                "lastName": user.last_name,
                "phoneNumber": user.phone,
                "dateOfBirth": user.born.isoformat(),
                "email": user.email,
            },
            "address": {
                "fullAddress": user.address,
            },
            "vendorData": str(user.id),
        }
    }

    headers = {
        "Content-Type": "application/json",
        "X-AUTH-CLIENT": settings.VERIFF_API_KEY,
    }

    veriff_api_url = settings.VERIFF_BASE_URL + "/v1/sessions"

    print(f"Sending to Veriff API: {payload}")
    r = requests.post(veriff_api_url, json=payload, headers=headers)
    print(f"Response from Veriff API: {r.text}")
    r.raise_for_status()
    data = r.json()

    # Add lang as query parameter to the session URL (per Veriff docs)
    session_url = data["verification"]["url"]
    if lang:
        session_url = f"{session_url}?lang={lang}"

    return session_url

def check_empty_fields(user: Union[Client, Satellite]):
    required_fields = {
        "firstName": user.name,
        "lastName": user.last_name,
        "phoneNumber": user.phone,
        "dateOfBirth": user.born,
        "email": user.email,
        "fullAddress": user.address,
    }
    empty_fields = [field for field, value in required_fields.items() if not value]
    if empty_fields:
        return empty_fields