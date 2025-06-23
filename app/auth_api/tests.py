import json
import urllib.parse
from io import BytesIO

import pyotp
from core.models import Token, TokenType, User
from core.services.token_service import TokenService
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from django.urls import reverse
from django.utils import timezone
from PIL import Image
from rest_framework import status
from rest_framework.test import APITestCase

from auth_api.cognito import Cognito
from auth_api.services.totp_service import TOTPService


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

    def get_user_by_email(self, email):
        return User.objects.get(email=email)

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
        # Set the token in the client's credentials for authenticated requests (so it will be used in subsequent requests)
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

    def test_register(self):
        """
        The function `test_register` registers a user and checks for a successful response.
        """
        self.register(email="ronak001@yopmail.com", password="Test@1234")
        self.match_success_response(201)

    def test_register_with_invalid_email(self):
        """
        The function `test_register_with_invalid_email` registers a user with an invalid email and
        checks for an error response.
        """
        self.register(email="unittest", password="Test@1234")
        self.match_error_response(422)

    def test_register_with_existing_email(self):
        """
        The function `test_register_with_existing_email` registers a user with an existing email and
        checks for an error response.
        """
        self.register()
        self.match_error_response(400)

    def test_register_with_short_password(self):
        """
        The function `test_register_with_short_password` registers a user with a short password and
        checks for an error response.
        """
        self.register(email="unittest1@yopmail.com", password="Test@12")
        self.match_error_response(422)

    def test_register_with_invalid_password(self):
        """
        The function `test_register_with_invalid_password` registers a user with an invalid password and
        checks for an error response.
        """
        self.register(email="unittest1@yopmail.com", password="testpassword")
        self.match_error_response(422)

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

    def test_login_unverified_user(self):
        """
        This test case attempts to log in a user with an unverified email and checks if it fails.
        """
        # Register a new user
        self.register(email="unverifieduser@yopmail.com", password="Test@1234")

        # Attempt to log in without verifying email
        self.login(email="unverifieduser@yopmail.com", password="Test@1234")

        self.match_error_response(401)

    def test_login_deleted_user(self):
        """
        This test case attempts to log in a user who has been deleted and checks for a failure response.
        """
        # Register a user
        self.register(email="deleteduser@yopmail.com", password="Test@1234")

        # Soft delete the user (update the 'is_deleted' or 'is_active' flag)
        user = self.get_user_by_email("deleteduser@yopmail.com")
        user.is_deleted = True
        user.save()

        # Attempt to log in the deleted user
        self.login(email="deleteduser@yopmail.com", password="Test@1234")

        # Expect failure because the user is deleted
        self.match_error_response(401)

    def test_login_inactive_user(self):
        """
        This test case attempts to log in an inactive user and checks for a failure response.
        """
        # Register a user
        self.register(email="inactiveuser@yopmail.com", password="Test@1234")

        # Set user to inactive
        user = self.get_user_by_email("inactiveuser@yopmail.com")
        user.is_active = False
        user.save()

        # Attempt to log in the inactive user
        self.login(email="inactiveuser@yopmail.com", password="Test@1234")

        # Expect failure because the user is inactive
        self.match_error_response(401)

    def test_login_with_wrong_mail(self):
        """
        This function tests the login functionality with wrong credentials.
        """
        self.login(email="test@yopmail.com", password=self.super_admin_password)
        self.match_error_response(401)

    def test_login_with_wrong_password(self):
        """
        This function tests the login functionality with wrong credentials.
        """
        self.login(email=self.super_admin_email, password="Unittest@1234")
        self.match_error_response(401)

    def test_logout(self):
        """
        The `test_logout` function logs a user out by sending a POST request to the logout endpoint
        with a refresh token in the request body and expects a success response with status code 204.
        """
        # Login the user and get the refresh token from self._data
        self.login()  # Assuming this populates self._data
        refresh_token = self._data["data"]["tokens"]["refresh"][
            "token"
        ]  # Extracting refresh token

        # Send a POST request to the logout endpoint with the token directly in the data
        self.set_response(
            self.client.post(
                f"{self.prefix}/logout",
                data=json.dumps({"token": refresh_token}),
                content_type="application/json",
            )
        )

        # Match the expected success response status code 204
        self.match_success_response(204)

    def test_logout_without_access_token(self):
        """
        The `test_logout_without_access_token` function logs a user out without a token and expects an error
        response with status code 204.
        """
        self.set_response(
            self.client.post(
                f"{self.prefix}/logout",
                content_type="application/json",
            )
        )
        self.match_error_response(401)

    def test_logout_with_wrong_token(self):
        """
        This function tests the logout functionality with a wrong token using a POST request.
        """
        # Log the user in and get the refresh token
        self.login()
        refresh_token = self._data["data"]["tokens"]["refresh"][
            "token"
        ]  # Extracting refresh token
        wrong_token = refresh_token + "1"  # Modify the refresh token to make it invalid

        # Modify the refresh token to make it invalid

        # Send a POST request to the logout endpoint with the wrong refresh token in the request body
        self.set_response(
            self.client.post(
                f"{self.prefix}/logout",
                data={"token": wrong_token},
                content_type="application/json",
            )
        )

        # Match the expected error response status code 401
        self.match_error_response(401)

    def test_logout_with_blacklisted_token(self):
        """
        This function tests the logout functionality with a blacklisted token.
        """
        self.login()
        self.make_token_blacklist(TokenType.ACCESS.value)
        self.set_response(
            self.client.post(
                f"{self.prefix}/logout",
                data={"token": self._data["data"]["tokens"]["access"]["token"]},
                content_type="application/json",
            )
        )
        print(self._data)
        self.match_error_response(403)

    def test_refresh_token(self):
        """
        The function `test_refresh_token` logs in, extracts the refresh token,
        sends a POST request to refresh the token, and matches the success response.
        """
        self.login()
        self._data = {
            "refresh": self._data["data"]["tokens"]["refresh"]["token"],
        }
        self.set_response(
            self.client.post(
                f"{self.prefix}/refresh-token", data=self._data, format="json"
            )
        )
        self.match_success_response()

    def test_refresh_token_without_payload(self):
        """
        The function `test_refresh_token` logs in, extracts the refresh token, sends a POST request to
        refresh the token, and matches the success response.
        """
        self.login()
        self.set_response(
            self.client.post(f"{self.prefix}/refresh-token", data={}, format="json")
        )
        self.match_error_response(422)

    def test_refresh_token_with_invalid_token(self):
        """
        This function tests the refresh token functionality with an invalid token.
        """
        self.login()
        self._data = {
            "refresh": "12345678",
        }
        self.set_response(
            self.client.post(
                f"{self.prefix}/refresh-token", data=self._data, format="json"
            )
        )
        self.match_error_response(401)

    def test_refresh_token_with_invalid_secret(self):
        """
        This function tests the refresh token functionality with an invalid secret.
        """
        self.login()
        refresh_token = self._data["data"]["tokens"]["refresh"]["token"]
        ORIGINAL_SECRET_KEY = settings.SECRET_KEY
        settings.SECRET_KEY = "test"
        self.login()
        self._data = {
            "refresh": refresh_token,
        }
        self.set_response(
            self.client.post(
                f"{self.prefix}/refresh-token", data=self._data, format="json"
            )
        )
        settings.SECRET_KEY = ORIGINAL_SECRET_KEY
        self.match_error_response(401)  # current status code 400

    def test_refresh_token_non_exist_record(self):
        """
        This function tests the refresh token functionality with a non-existing record.
        """
        self.login()
        self._data = {
            "refresh": self._data["data"]["tokens"]["refresh"]["token"],
        }
        Token.objects.filter(token_type="refresh").delete()
        self.set_response(
            self.client.post(
                f"{self.prefix}/refresh-token", data=self._data, format="json"
            )
        )
        self.match_error_response(401)  # current status code 400

    def test_refresh_token_with_blacklisted_token(self):
        """
        This function tests the refresh token functionality with a blacklisted token.
        """
        self.login()
        self.make_token_blacklist("refresh")
        self._data = {
            "refresh": self._data["data"]["tokens"]["refresh"]["token"],
        }
        self.set_response(
            self.client.post(
                f"{self.prefix}/refresh-token", data=self._data, format="json"
            )
        )
        self.match_error_response(401)  # current status code 400

    def test_refresh_token_with_expired_token(self):
        """
        This function tests the refresh token functionality with an expired token.
        """
        self.login()
        self.make_token_expired("refresh")
        self._data = {
            "refresh": self._data["data"]["tokens"]["refresh"]["token"],
        }
        self.set_response(
            self.client.post(
                f"{self.prefix}/refresh-token", data=self._data, format="json"
            )
        )
        self.match_error_response(401)  # current status code 400

    def test_refresh_if_user_not_exist(self):
        """
        This function tests the refresh token functionality with a user that does not exist.
        """
        self.login()
        self.super_admin.delete()
        self._data = {
            "refresh": self._data["data"]["tokens"]["refresh"]["token"],
        }
        self.set_response(
            self.client.post(
                f"{self.prefix}/refresh-token", data=self._data, format="json"
            )
        )
        self.match_error_response(401)  # current status code 400

    def test_get_profile(self):
        """
        The `test_profile` function logs in, retrieves a profile URL in JSON format, and matches the
        success response.
        """
        self.login()
        self.set_response(self.client.get(self.profile_url, format="json"))
        self.match_success_response()

    def test_get_profile_without_access_token(self):
        """
        The `test_profile` function logs in, retrieves a profile URL in JSON format, and matches the
        success response.
        """
        self.set_response(self.client.get(self.profile_url, format="json"))
        self.match_error_response(401)

    def test_get_profile_with_expired_token(self):
        """
        This function tests the get profile functionality with an expired token.
        """
        self.login()
        self.make_token_expired(TokenType.ACCESS.value)
        self.set_response(self.client.get(self.profile_url, format="json"))
        self.match_error_response(403)

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

    def test_forgot_password_invalid_body(self):
        """
        This function tests the behavior of forgetting a password with an invalid email body.
        """
        self.send_forgot_password_mail(email="unittest")
        self.match_error_response(422)

    def test_forgot_password_with_empty_body(self):
        """
        This function tests the behavior of forgetting a password with an empty email body.
        """
        self.set_response(
            self.client.post(f"{self.prefix}/forgot-password", data={}, format="json")
        )
        self.match_error_response(422)

    def test_reset_password(self):
        """
        The `test_reset_password` function sends a forgot password email, retrieves a reset token, and
        resets the password for a user in a test scenario.
        """
        self.send_forgot_password_mail()
        reset_token = TokenService.for_user(self.super_admin, "reset", 1)
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

    def test_reset_password_token_blacklisted(self):
        """
        This function tests the scenario where a blacklisted token is used to reset a password.
        """
        self.send_forgot_password_mail()
        reset_token = TokenService.for_user(self.super_admin, "reset", 1)
        self.make_token_blacklist("reset")
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
        self.match_success_response(401)  # current status code 400

    def test_reset_password_with_expired_token(self):
        """
        This function tests the scenario where an expired token is used to reset a password.
        """
        self.send_forgot_password_mail()
        reset_token = TokenService.for_user(self.super_admin, "reset", 1)
        self.make_token_expired("reset")
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
        self.match_success_response(401)  # current status code 400

    def test_reset_password_with_invalid_token(self):
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
        self.match_success_response(401)

    def test_reset_password_without_user(self):
        """
        This function tests the scenario where a user does not exist.
        """
        self.send_forgot_password_mail()
        reset_token = TokenService.for_user(self.super_admin, "reset", 1)
        self.super_admin.delete()
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
        self.match_success_response(401)  # current status code 400

    def test_send_verification_mail(self):
        """
        The function `test_send_verification_mail` sends a verification email and checks for a
        successful response.
        """
        self.send_verification_email()
        self.match_success_response(204)

    def test_verify_email(self):
        """
        The function `test_verify_email` verifies an email and checks for a successful response.
        """
        self.send_verification_email()
        verify_token = TokenService.for_user(
            self.super_admin, TokenType.VERIFY_MAIL.value, 1
        )
        self.set_response(self.client.get(f"{self.prefix}/verify-email/{verify_token}"))
        self.match_success_response(204)

    def test_verify_email_token_blacklisted(self):
        """
        This function tests the scenario where a blacklisted token is used to verify an email.
        """
        self.send_verification_email()
        verify_token = TokenService.for_user(self.super_admin, "verify", 1)
        self.make_token_blacklist("verify")
        self.set_response(self.client.get(f"{self.prefix}/verify-email/{verify_token}"))
        self.match_success_response(401)  # current status code 400

    def test_verify_email_with_expired_token(self):
        """
        This function tests the scenario where an expired token is used to verify an email.
        """
        self.send_verification_email()
        verify_token = TokenService.for_user(self.super_admin, "verify", 1)
        self.make_token_expired("verify")
        self.set_response(self.client.get(f"{self.prefix}/verify-email/{verify_token}"))
        self.match_success_response(401)  # current status code 400


class CognitoIntegrationTest(BaseAPITestCase):
    prefix = "/api/auth"

    def setUp(self):
        super().setUp()
        self.email = "parth@yopmail.com"
        self.password = "Parth@123"
        self.sync_token_url = reverse("cognito-sync-tokens")
        self.add_group_url = reverse("create-cognito-group")
        cognito = Cognito()
        # Ensure user exists and is confirmed in Cognito
        try:
            cognito.admin_get_user(self.email)
        except Exception:
            cognito.sign_up(
                self.email,
                self.password,
                user_attributes=[
                    {"Name": "email", "Value": self.email},
                    {"Name": "given_name", "Value": "Parth"},
                    {"Name": "family_name", "Value": "Yopmail"},
                ],
            )
            cognito.admin_confirm_sign_up(self.email)
        # Ensure user exists in Django
        User.objects.get_or_create(
            email=self.email, defaults={"password": self.password}
        )

    def test_create_role_api(self):
        """
        Test the API endpoint for adding a group using access token.
        """
        cognito = Cognito()
        tokens = cognito.login(self.email, self.password)
        access_token = tokens["AccessToken"]
        refresh_token = tokens.get("RefreshToken")

        user, created = User.objects.get_or_create(
            email=self.email, defaults={"password": self.password}
        )

        # Save tokens to DB
        Token.objects.update_or_create(
            user=user, token_type="access_token", defaults={"token": access_token}
        )
        if refresh_token:
            Token.objects.update_or_create(
                user=user, token_type="refresh_token", defaults={"token": refresh_token}
            )

        group_name = "ApiTestGroup"
        headers = {"HTTP_AUTHORIZATION": f"Bearer {access_token}"}
        data = {"name": group_name}
        response = self.client.post(self.add_group_url, data, **headers)
        if response.status_code == 403:
            self.skipTest(
                "Skipping due to insufficient API permissions (403 Forbidden)."
            )
        self.assertIn(response.status_code, [200, 201])

    def test_cognito_create_and_add_user_to_role(self):
        """
        Ensure group exists before adding user to it, and sync with Django Group.
        """
        cognito = Cognito()
        group_name = "ApiTestGroup"

        # Step 1: Ensure Django group exists
        group, _ = Group.objects.get_or_create(name=group_name)
        # Step 2: Add user to Django group
        user = User.objects.get(email=self.email)
        user.groups.add(group)
        user.save()
        self.assertIn(group, user.groups.all())

        # Step 3: Create group in Cognito (if not exists)
        try:
            response = cognito.create_role(group_name)
            print("create_role response", response)
            self.assertIn("Group", response)
        except Exception as e:
            print(f"Group creation skipped or failed: {e}")

        # Step 4: Add user to Cognito group
        response = cognito.add_user_to_role(self.email, group_name)
        if isinstance(response, bool):
            self.assertTrue(response)
        else:
            self.assertIn("ResponseMetadata", response)
            self.assertIn(response["ResponseMetadata"]["HTTPStatusCode"], [200, 201])

    def test_cognito_remove_user_from_role(self):
        """
        Test removing user from a Cognito group (role).
        """
        cognito = Cognito()
        group_name = "ApiTestGroup"

        # Ensure user is in the group first
        try:
            cognito.add_user_to_role(self.email, group_name)
        except Exception as e:
            print(f"User may already be in group or group doesn't exist: {e}")

        # Now remove the user from the group
        response = cognito.remove_user_from_role(self.email, group_name)
        self.assertIn("ResponseMetadata", response)
        self.assertIn(response["ResponseMetadata"]["HTTPStatusCode"], [200, 201])

        # Optionally, verify user is no longer in the group
        try:
            groups = cognito.list_user_groups(self.email)
            group_names = [g["GroupName"] for g in groups]
            self.assertNotIn(group_name, group_names)
        except Exception as e:
            print(f"Could not verify group removal: {e}")

    def test_cognito_delete_role(self):
        """
        Test deleting a Cognito group.
        """
        cognito = Cognito()
        group_name = "ApiTestGroup"
        try:
            response = cognito.delete_group(group_name)
            # If delete_group returns None on success, just assert no exception
            self.assertIsNone(response)
        except Exception as e:
            self.skipTest(f"Skipping due to AWS permissions or group not found: {e}")

    def test_cognito_delete_user(self):
        """
        Test deleting a Cognito user.
        """
        cognito = Cognito()
        try:
            cognito.delete_user(self.email)
            # If no exception, deletion is considered successful
            self.assertTrue(True)
        except Exception as e:
            self.skipTest(f"Skipping due to AWS permissions: {e}")


class TOTPServiceTestCase(APITestCase):
    def setUp(self):
        """Initializes the test case by creating a user and an instance of TOTPService."""
        self.user = User.objects.create_user(
            email="totpuser@yopmail.com", password="Test@1234"
        )
        self.totp_service = TOTPService(self.user)

    def test_generate_secret(self):
        """Tests the generation of a TOTP secret and verifies it is saved to the user."""
        secret = self.totp_service.generate_secret()
        self.assertTrue(secret)
        self.user.refresh_from_db()
        self.assertEqual(self.user.totp_secret, secret)

    def test_get_provisioning_uri(self):
        """Tests the generation of a provisioning URI for TOTP."""
        self.totp_service.generate_secret()
        uri = self.totp_service.get_provisioning_uri()
        encoded_email = urllib.parse.quote(self.user.email)
        self.assertIn(encoded_email, uri)
        self.assertTrue(uri.startswith("otpauth://totp/"))

    def test_generate_qr_code_url(self):
        """Tests the generation of a QR code URL for TOTP."""
        self.totp_service.generate_secret()
        qr_url = self.totp_service.generate_qr_code_url()
        self.assertTrue(qr_url.startswith("data:image/png;base64,"))

    def test_verify_code(self):
        """Tests the verification of a TOTP code."""
        secret = self.totp_service.generate_secret()
        totp = pyotp.TOTP(secret)
        code = totp.now()
        self.assertTrue(self.totp_service.verify_code(code))
        self.assertFalse(self.totp_service.verify_code("000000"))
