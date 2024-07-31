from django.conf import settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from auth_api.models import User


# Create your tests here.
class AuthAPIRateLimitTestCase(APITestCase):
    def setUp(self):
        user_email = "testuser@example.com"
        user_password = "testpass123"
        self.user = User.objects.create_superuser(
            email=user_email,
            name="Test User",
            password=user_password,
            tc=True,
        )
        self.user.is_active = True
        self.user.save()

        self.client = APIClient()
        self.login_url = reverse("login")
        self.profile_url = reverse("profile")

        self.limit = int(settings.AUTH_THROTTLING_LIMIT.split("/")[0])
        login_response = self.client.post(
            self.login_url,
            {"email": user_email, "password": user_password},
            format="json",
        )
        # Extract access token
        self.access_token = login_response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.access_token)

        self.verify_email = reverse("verify-email", kwargs={"token": self.access_token})

    def test_auth_user_ratelimit(self):
        for _ in range(self.limit + 1):
            response = self.client.post(self.profile_url)

        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_auth_annon_ratelimit(self):
        self.client = APIClient()
        self.client.credentials()

        for _ in range(self.limit + 1):
            response = self.client.post(self.profile_url)

        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
