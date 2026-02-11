from django.test import TestCase, override_settings
from unittest.mock import patch
from django.urls import reverse
from django.core import mail
from user.client.models import Client
from user.client.api.frontend.utils import create_veriff_session, send_email_message_verification
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
import datetime

class VeriffUtilsTests(TestCase):
    def test_create_veriff_session(self):
        user = Client.objects.create(
            username="testuser",
            email="test@example.com",
            name="Test",
            last_name="User",
            city="Test City",
            country="Test Country",
            address="123 Test St",
            born=datetime.date(1990, 1, 1),
            phone="1234567890",
            invitation_code="INVITE1234",
            allow_password_update=True,
            ip="128.84.84.84",
            password="securepassword123",
        )

        fake_url = "https://veriff.com/session/123"
        def fake_post(url, json, headers):
            class Resp:
                def raise_for_status(self): pass
                def json(self):
                    return {"verification": {"url": fake_url}}
            return Resp()
        with patch("requests.post", fake_post):
            url = create_veriff_session(user)
        self.assertEqual(url, fake_url)

    @override_settings(EMAIL_HOST_USER="noreply@example.com")
    def test_send_email_message_verification(self):
        user = Client.objects.create(
            username="testuser2",
            email="test2@example.com",
            name="Test2",
            last_name="User2",
            city="Test City",
            country="Test Country",
            address="123 Test St",
            born=datetime.date(1990, 1, 1),
            phone="1234567890",
            invitation_code="INVITE1234",
            allow_password_update=True,
            ip="128.84.84.84",
            password="securepassword123",
        )
        activate_url = "https://example.com/activate"
        send_email_message_verification(user, activate_url)
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertIn(user.email, email.to)
        self.assertIn("Підтвердіть свій Email", email.subject)
        self.assertIn(activate_url, email.alternatives[0][0])

class StartVerificationSessionAPITest(TestCase):
    def setUp(self):
        self.password = "testpass123"
        self.user = Client.objects.create_user(
            username="apitestuser",
            email="apitest@example.com",
            password=self.password,
            name="Api",
            last_name="User",
            city="Test City",
            country="Test Country",
            address="123 Test St",
            born=datetime.date(1990, 1, 1),
            phone="1234567890",
            invitation_code="INVITE1234",
            allow_password_update=True,
            ip="128.84.84.84",
        )
        self.client = APIClient()
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(refresh.access_token))

    # @patch("user.client.api.frontend.views.views.create_veriff_session")
    def test_start_verification_session(self):
        url = reverse("start-verification-session")
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("session_url", response.json())
        print("session_url:", response.json()["session_url"])
        # self.assertEqual(response.json()["session_url"], "https://veriff.com/session/456")