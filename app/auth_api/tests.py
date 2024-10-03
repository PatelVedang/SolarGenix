from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from django.urls import reverse
from django.utils import timezone
from PIL import Image
from rest_framework import status
from rest_framework.test import APITestCase

from auth_api.models import SimpleToken, Token, User


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
        print("-------", self.status_code, "<----------")
        self.assertEqual(
            self.status_code,
            status_code if status_code else status.HTTP_400_BAD_REQUEST,
        )

    def register(self, email=None, password=None):
        self._data = {
            "email": email or self.super_admin_email,
            "first_name": "unittest",
            "last_name": "unittest",
            "password": password or self.super_admin_password,
            "confirm_password": password or self.super_admin_password,
        }
        self.set_response(
            self.client.post(f"{self.prefix}/register", data=self._data, format="json")
        )

    # def login(self, email=None, password=None):
    #     self._data = {
    #         "email": email or self.super_admin_email,
    #         "password": password or self.super_admin_password,
    #     }
    #     # super_user = User.objects.get(email=self.)
    #     self.set_response(
    #         self.client.post(self.login_url, data=self._data, format="json")
    #     )
    #     self.client.credentials(
    #         HTTP_AUTHORIZATION=f"Bearer {self._data.get('data',{}).get('access',{}).get('token','')}"
    #     )

    def login(self, email=None, password=None):
        self._data = {
            "email": email or self.super_admin_email,
            "password": password or self.super_admin_password,
        }

        # Make the login request
        response = self.client.post(self.login_url, data=self._data, format="json")

        # Set the response for future assertions if needed
        self.set_response(response)

        # Extract the token from the response
        token = (
            response.data.get("data", {})
            .get("tokens", {})
            .get("access", {})
            .get("token", "")
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

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

    def make_token_blacklist(self, token_type):
        token = Token.objects.get(
            user=self.super_admin,
            token_type=token_type,
            is_blacklist_at__isnull=True,
        )
        token.is_blacklist_at = timezone.now()
        token.save()

    def make_token_expired(self, token_type):
        token = Token.objects.get(
            user=self.super_admin,
            token_type=token_type,
            is_blacklist_at__isnull=True,
        )
        token.expire_at = token.expire_at - timezone.timedelta(days=1000)
        token.save()

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

    # def test_register(self):
    #     """
    #     The function `test_register` registers a user and checks for a successful response.
    #     """
    #     self.register(email="unittest1@yopmail.com", password="Test@1234")
    #     self.match_success_response(201)

    # def test_register_with_invalid_email(self):
    #     """
    #     The function `test_register_with_invalid_email` registers a user with an invalid email and
    #     checks for an error response.
    #     """
    #     self.register(email="unittest", password="Test@1234")
    #     self.match_error_response(422)

    # def test_register_with_existing_email(self):
    #     """
    #     The function `test_register_with_existing_email` registers a user with an existing email and
    #     checks for an error response.
    #     """
    #     self.register()
    #     self.match_error_response(400)

    # def test_register_with_short_password(self):
    #     """
    #     The function `test_register_with_short_password` registers a user with a short password and
    #     checks for an error response.
    #     """
    #     self.register(email="unittest1@yopmail.com", password="Test@12")
    #     self.match_error_response(422)

    # def test_register_with_invalid_password(self):
    #     """
    #     The function `test_register_with_invalid_password` registers a user with an invalid password and
    #     checks for an error response.
    #     """
    #     self.register(email="unittest1@yopmail.com", password="testpassword")
    #     self.match_error_response(422)

    # def test_send_verification_email(self):
    #     """
    #     The function `test_send_verification_email` sends a verification email and checks for a
    #     successful response.
    #     """
    #     self.send_verification_email()
    #     self.match_success_response(204)

    # def test_login(self):
    #     """
    #     This function tests the login functionality by calling the login method and verifying the
    #     success response.
    #     """
    #     self.login()
    #     self.match_success_response()

    # def test_login_with_wrong_mail(self):
    #     """
    #     This function tests the login functionality with wrong credentials.
    #     """
    #     self.login(email="test@yopmail.com", password=self.super_admin_password)
    #     self.match_error_response(401)

    # def test_login_with_wrong_password(self):
    #     """
    #     This function tests the login functionality with wrong credentials.
    #     """
    #     self.login(email=self.super_admin_email, password="Unittest@1234")
    #     self.match_error_response(401)

    # def test_logout(self):
    #     """
    #     The `test_logout` function logs a user out by sending a GET request to the logout endpoint and
    #     expects a success response with status code 204.
    #     """
    #     self.login()
    #     self.set_response(self.client.get(f"{self.prefix}/logout"))
    #     self.match_success_response(204)

    # def test_logout_without_access_token(self):
    #     """
    #     The `test_logout_without_access_token` function logs a user out without a token and expects an error
    #     response with status code 401.
    #     """
    #     self.set_response(self.client.get(f"{self.prefix}/logout"))
    #     self.match_error_response(401)

    # def test_logout_with_expired_token(self):
    #     """
    #     This function tests the logout functionality with an expired token.
    #     """
    #     self.login()
    #     self.make_token_expired(TokenType.ACCESS.value)
    #     self.set_response(self.client.get(f"{self.prefix}/logout"))
    #     self.match_error_response(204)  # current status code 403

    # def test_logout_with_blacklisted_token(self):
    #     """
    #     This function tests the logout functionality with a blacklisted token.
    #     """
    #     self.login()
    #     self.make_token_blacklist(TokenType.ACCESS.value)
    #     self.set_response(self.client.get(f"{self.prefix}/logout"))
    #     self.match_error_response(401)  # current status code 403

    # def test_logout_with_wrong_token(self):
    #     """
    #     This function tests the logout functionality with a wrong token.
    #     """
    #     self.login()
    #     self.client.credentials(
    #         HTTP_AUTHORIZATION=f"Bearer {self._data.get('data',{}).get('access',{}).get('token','')}1"
    #     )
    #     self.set_response(self.client.get(f"{self.prefix}/logout"))
    #     self.match_error_response(401)

    # def test_refresh_token(self):
    #     """
    #     The function `test_refresh_token` logs in, extracts the refresh token,
    #     sends a POST request to refresh the token, and matches the success response.
    #     """
    #     self.login()
    #     self._data = {
    #         "refresh": self._data["data"]["tokens"]["refresh"]["token"],
    #     }
    #     self.set_response(
    #         self.client.post(
    #             f"{self.prefix}/refresh-token", data=self._data, format="json"
    #         )
    #     )
    #     self.match_success_response()

    # def test_refresh_token_without_payload(self):
    #     """
    #     The function `test_refresh_token` logs in, extracts the refresh token, sends a POST request to
    #     refresh the token, and matches the success response.
    #     """
    #     self.login()
    #     self.set_response(
    #         self.client.post(f"{self.prefix}/refresh-token", data={}, format="json")
    #     )
    #     self.match_error_response(422)

    # def test_refresh_token_with_invalid_token(self):
    #     """
    #     This function tests the refresh token functionality with an invalid token.
    #     """
    #     self.login()
    #     self._data = {
    #         "refresh": "12345678",
    #     }
    #     self.set_response(
    #         self.client.post(
    #             f"{self.prefix}/refresh-token", data=self._data, format="json"
    #         )
    #     )
    #     self.match_error_response(401)

    # def test_refresh_token_with_invalid_secret(self):
    #     """
    #     This function tests the refresh token functionality with an invalid secret.
    #     """
    #     self.login()
    #     refresh_token = self._data["data"]["tokens"]["refresh"]["token"]
    #     ORIGINAL_SECRET_KEY = settings.SECRET_KEY
    #     settings.SECRET_KEY = "test"
    #     self.login()
    #     self._data = {
    #         "refresh": refresh_token,
    #     }
    #     self.set_response(
    #         self.client.post(
    #             f"{self.prefix}/refresh-token", data=self._data, format="json"
    #         )
    #     )
    #     settings.SECRET_KEY = ORIGINAL_SECRET_KEY
    #     self.match_error_response(401)  # current status code 400

    # def test_refresh_token_non_exist_record(self):
    #     """
    #     This function tests the refresh token functionality with a non-existing record.
    #     """
    #     self.login()
    #     self._data = {
    #         "refresh": self._data["data"]["tokens"]["refresh"]["token"],
    #     }
    #     Token.objects.filter(token_type="refresh").delete()
    #     self.set_response(
    #         self.client.post(
    #             f"{self.prefix}/refresh-token", data=self._data, format="json"
    #         )
    #     )
    #     self.match_error_response(401)  # current status code 400

    # def test_refresh_token_with_blacklisted_token(self):
    #     """
    #     This function tests the refresh token functionality with a blacklisted token.
    #     """
    #     self.login()
    #     self.make_token_blacklist("refresh")
    #     self._data = {
    #         "refresh": self._data["data"]["tokens"]["refresh"]["token"],
    #     }
    #     self.set_response(
    #         self.client.post(
    #             f"{self.prefix}/refresh-token", data=self._data, format="json"
    #         )
    #     )
    #     self.match_error_response(401)  # current status code 400

    # def test_refresh_token_with_expired_token(self):
    #     """
    #     This function tests the refresh token functionality with an expired token.
    #     """
    #     self.login()
    #     self.make_token_expired("refresh")
    #     self._data = {
    #         "refresh": self._data["data"]["tokens"]["refresh"]["token"],
    #     }
    #     self.set_response(
    #         self.client.post(
    #             f"{self.prefix}/refresh-token", data=self._data, format="json"
    #         )
    #     )
    #     self.match_error_response(401)  # current status code 400

    # def test_refresh_if_user_not_exist(self):
    #     """
    #     This function tests the refresh token functionality with a user that does not exist.
    #     """
    #     self.login()
    #     self.super_admin.delete()
    #     self._data = {
    #         "refresh": self._data["data"]["tokens"]["refresh"]["token"],
    #     }
    #     self.set_response(
    #         self.client.post(
    #             f"{self.prefix}/refresh-token", data=self._data, format="json"
    #         )
    #     )
    #     self.match_error_response(401)  # current status code 400

    # def test_get_profile(self):
    #     """
    #     The `test_profile` function logs in, retrieves a profile URL in JSON format, and matches the
    #     success response.
    #     """
    #     self.login()
    #     self.set_response(self.client.get(self.profile_url, format="json"))
    #     self.match_success_response()

    # def test_get_profile_without_access_token(self):
    #     """
    #     The `test_profile` function logs in, retrieves a profile URL in JSON format, and matches the
    #     success response.
    #     """
    #     self.set_response(self.client.get(self.profile_url, format="json"))
    #     self.match_error_response(401)

    # def test_get_profile_with_expired_token(self):
    #     """
    #     This function tests the get profile functionality with an expired token.
    #     """
    #     self.login()
    #     self.make_token_expired(TokenType.ACCESS.value)
    #     self.set_response(self.client.get(self.profile_url, format="json"))
    #     self.match_error_response(403)

    # def test_forgot_password(self):
    #     """
    #     The function test_forgot_password sends a forgot password email and checks for a successful
    #     response.
    #     """
    #     self.send_forgot_password_mail()
    #     self.match_success_response(204)

    # def test_forgot_mail_not_exist(self):
    #     """
    #     The function sends a forgot password email to a specified email address and expects a 204 error
    #     response.
    #     """
    #     self.send_forgot_password_mail(email="dummy@yopmail.com")
    #     self.match_error_response(204)

    # def test_forgot_password_invalid_body(self):
    #     """
    #     This function tests the behavior of forgetting a password with an invalid email body.
    #     """
    #     self.send_forgot_password_mail(email="unittest")
    #     self.match_error_response(422)

    # def test_forgot_password_with_empty_body(self):
    #     """
    #     This function tests the behavior of forgetting a password with an empty email body.
    #     """
    #     self.set_response(
    #         self.client.post(f"{self.prefix}/forgot-password", data={}, format="json")
    #     )
    #     self.match_error_response(422)

    # def test_reset_password(self):
    #     """
    #     The `test_reset_password` function sends a forgot password email, retrieves a reset token, and
    #     resets the password for a user in a test scenario.
    #     """
    #     self.send_forgot_password_mail()
    #     reset_token = SimpleToken.for_user(self.super_admin, "reset", 1)
    #     self._data = {
    #         "password": self.super_admin_password,
    #         "confirm_password": self.super_admin_password,
    #     }
    #     self.set_response(
    #         self.client.post(
    #             f"{self.prefix}/reset-password/{reset_token}",
    #             data=self._data,
    #             format="json",
    #         )
    #     )
    #     self.match_success_response(204)

    # def test_reset_password_token_blacklisted(self):
    #     """
    #     This function tests the scenario where a blacklisted token is used to reset a password.
    #     """
    #     self.send_forgot_password_mail()
    #     reset_token = SimpleToken.for_user(self.super_admin, "reset", 1)
    #     self.make_token_blacklist("reset")
    #     self._data = {
    #         "password": self.super_admin_password,
    #         "confirm_password": self.super_admin_password,
    #     }
    #     self.set_response(
    #         self.client.post(
    #             f"{self.prefix}/reset-password/{reset_token}",
    #             data=self._data,
    #             format="json",
    #         )
    #     )
    #     self.match_success_response(401)  # current status code 400

    def test_reset_password_with_expired_token(self):
        """
        This function tests the scenario where an expired token is used to reset a password.
        """
        self.send_forgot_password_mail()
        reset_token = SimpleToken.for_user(self.super_admin, "reset", 1)
        self.make_token_expired("reset")
        self._data = {
            "password": self.super_admin_password,
            "confirm_password": self.super_admin_password,
        }
        print("---------------------------------------------------")
        print(reset_token)

        self.set_response(
            self.client.post(
                f"{self.prefix}/reset-password/{reset_token}",
                data=self._data,
                format="json",
            )
        )
        self.match_success_response(401)  # current status code 400

    # def test_reset_password_with_invalid_token(self):
    #     """
    #     This function tests the scenario where an invalid token is used to reset a password.
    #     """
    #     self._data = {
    #         "password": self.super_admin_password,
    #         "confirm_password": self.super_admin_password,
    #     }
    #     self.set_response(
    #         self.client.post(
    #             f"{self.prefix}/reset-password/1234", data=self._data, format="json"
    #         )
    #     )
    #     self.match_success_response(400)

    # def test_reset_password_without_user(self):
    #     """
    #     This function tests the scenario where a user does not exist.
    #     """
    #     self.send_forgot_password_mail()
    #     reset_token = SimpleToken.for_user(self.super_admin, "reset", 1)
    #     self.super_admin.delete()
    #     self._data = {
    #         "password": self.super_admin_password,
    #         "confirm_password": self.super_admin_password,
    #     }
    #     self.set_response(
    #         self.client.post(
    #             f"{self.prefix}/reset-password/{reset_token}",
    #             data=self._data,
    #             format="json",
    #         )
    #     )
    #     self.match_success_response(401)  # current status code 400

    # def test_send_verification_mail(self):
    #     """
    #     The function `test_send_verification_mail` sends a verification email and checks for a
    #     successful response.
    #     """
    #     self.send_verification_email()
    #     self.match_success_response(204)

    # def test_verify_email(self):
    #     """
    #     The function `test_verify_email` verifies an email and checks for a successful response.
    #     """
    #     self.send_verification_email()
    #     verify_token = SimpleToken.for_user(
    #         self.super_admin, TokenType.VERIFY_MAIL.value, 1
    #     )
    #     self.set_response(self.client.get(f"{self.prefix}/verify-email/{verify_token}"))
    #     self.match_success_response(204)

    # def test_verify_email_token_blacklisted(self):
    #     """
    #     This function tests the scenario where a blacklisted token is used to verify an email.
    #     """
    #     self.send_verification_email()
    #     verify_token = SimpleToken.for_user(self.super_admin, "verify", 1)
    #     self.make_token_blacklist("verify")
    #     self.set_response(self.client.get(f"{self.prefix}/verify-email/{verify_token}"))
    #     self.match_success_response(401)  # current status code 400

    # def test_verify_email_with_expired_token(self):
    #     """
    #     This function tests the scenario where an expired token is used to verify an email.
    #     """
    #     self.send_verification_email()
    #     verify_token = SimpleToken.for_user(self.super_admin, "verify", 1)
    #     self.make_token_expired("verify")
    #     self.set_response(self.client.get(f"{self.prefix}/verify-email/{verify_token}"))
    #     self.match_success_response(401)  # current status code 400
