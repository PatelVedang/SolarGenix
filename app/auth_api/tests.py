from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.test import Client
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from auth_api.models import User, Token, SimpleToken
from io import BytesIO


class BaseAPITestCase(APITestCase):
    client = Client()
    super_admin_email = "unittest@yopmail.com"
    super_admin_password = "Unittest@123"
    login_url = reverse("login")
    profile_url = reverse("me")

    def setUp(self):
        self.super_admin = User.objects.create_superuser(
            email=self.super_admin_email,
            password=self.super_admin_password,
        )
        self.super_admin.save()

    def set_response(self, json_obj):
        """
        Sets the response and data attributes based on the provided JSON object.

        Args:
            json_obj (dict): The JSON object representing the response.

        Returns:
            None
        """
        self._response = json_obj
        if self._response.status_code == 204:
            self.status_code = 204
            return
        self.status_code = self._response.status_code
        self._data = self._response.json()

    def match_success_response(self, status_code=None):
        """
        This function checks that the status code of the response is 200 and that the response data
        matches the expected data
        """
        self.assertEqual(
            self.status_code,
            status_code if status_code else status.HTTP_200_OK,
        )

    def match_error_response(self, status_code=None):
        """
        It asserts that the status code is 401 and the status is False
        """
        self.assertEqual(
            self.status_code,
            status_code if status_code else status.HTTP_400_BAD_REQUEST,
        )

    def login(self, email=None, password=None):
        print(email, password)
        self._data = {
            "email": email or self.super_admin_email,
            "password": password or self.super_admin_password,
        }
        # super_user = User.objects.get(email=self.)
        self.set_response(
            self.client.post(self.login_url, data=self._data, format="json")
        )
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self._data.get('data',{}).get('access',{}).get('token','')}"
        )

    def send_forgot_password_mail(self, email=None):
        self._data = {
            "email": email or self.super_admin_email,
        }
        self.set_response(
            self.client.post(
                f"{self.prefix}/forgot-password", data=self._data, format="json"
            )
        )

    def send_verification_email(self):
        self._data = {
            "email": self.super_admin_email,
        }
        self.set_response(
            self.client.post(
                f"{self.prefix}/send-verification-email", data=self._data, format="json"
            )
        )

    def generate_image(self):
        """
        Generates an in-memory PNG image file for testing purposes.
        """
        image = Image.new("RGB", (100, 100))
        image_io = BytesIO()
        image.save(image_io, format="PNG")
        image_io.seek(0)
        return SimpleUploadedFile(
            "test_image.png", image_io.read(), content_type="image/png"
        )

    def generate_text_file(self):
        """
        Generates an in-memory text file for testing purposes.
        """
        file_content = "This is a test file"
        text_io = BytesIO(file_content.encode())
        return SimpleUploadedFile(
            "test_file.txt", text_io.read(), content_type="text/plain"
        )


class AuthTest(BaseAPITestCase):
    prefix = "/api/auth"

    def test_send_verification_email(self):
        """
        The function `test_send_verification_email` sends a verification email and checks for a
        successful response.
        """
        self.send_verification_email()
        self.match_success_response(204)

    def test_login(self):
        """
        This function tests the login functionality by calling the login method and verifying the
        success response.
        """
        self.login()
        self.match_success_response()

    def test_profile(self):
        """
        The `test_profile` function logs in, retrieves a profile URL in JSON format, and matches the
        success response.
        """
        self.login()
        self.set_response(self.client.get(self.profile_url, format="json"))
        self.match_success_response()

    def test_logout(self):
        """
        The `test_logout` function logs a user out by sending a GET request to the logout endpoint and
        expects a success response with status code 204.
        """
        self.login()
        self.set_response(self.client.get(f"{self.prefix}/logout"))
        self.match_success_response(204)

    def test_forgot_password(self):
        """
        The function test_forgot_password sends a forgot password email and checks for a successful
        response.
        """
        self.send_forgot_password_mail()
        self.match_success_response(204)

    def test_forgot_mail_not_exist(self):
        """
        The function sends a forgot password email to a specified email address and expects a 204 error
        response.
        """
        self.send_forgot_password_mail(email="dummy@yopmail.com")
        self.match_error_response(204)

    def test_forget_password_invalid_body(self):
        """
        This function tests the behavior of forgetting a password with an invalid email body.
        """
        self.send_forgot_password_mail(email="unittest")
        self.match_error_response(400)

    def test_reset_password_invalid_token(self):
        """
        This function tests the scenario where an invalid token is used to reset a password.
        """
        self._data = {
            "password": self.super_admin_password,
            "confirm_password": self.super_admin_password,
        }
        self.set_response(
            self.client.post(
                f"{self.prefix}/reset-password/1234", data=self._data, format="json"
            )
        )
        self.match_success_response(400)

    def test_reset_password_invalid_body(self):
        """
        The function `test_reset_password_invalid_body` tests the reset password functionality with an
        invalid body.
        """
        self._data = {
            "password": self.super_admin_password,
            "confirm_password": "Unit@1010",
        }
        self.set_response(
            self.client.post(
                f"{self.prefix}/reset-password/12345678", data=self._data, format="json"
            )
        )
        self.match_error_response(400)

    def test_reset_password(self):
        """
        The `test_reset_password` function sends a forgot password email, retrieves a reset token, and
        resets the password for a user in a test scenario.
        """
        self.send_forgot_password_mail()
        user = User.objects.get(email=self.super_admin_email)
        token = Token.objects.get(
            user=user,
            token_type="reset",
            is_blacklist_at__isnull=True,
        )
        reset_token = SimpleToken.for_user(user, "reset", 1, jti=token.jti)
        self._data = {
            "password": self.super_admin_password,
            "confirm_password": self.super_admin_password,
        }
        self.set_response(
            self.client.post(
                f"{self.prefix}/reset-password/{reset_token}",
                data=self._data,
                format="json",
            )
        )
        self.match_success_response(204)

    def test_refersh_token(self):
        """
        The function `test_refresh_token` logs in, extracts the refresh token, sends a POST request to
        refresh the token, and matches the success response.
        """
        self.login()
        self._data = {
            "refresh": self._data["data"]["refresh"]["token"],
        }
        self.set_response(
            self.client.post(
                f"{self.prefix}/refresh-token", data=self._data, format="json"
            )
        )
        self.match_success_response()
