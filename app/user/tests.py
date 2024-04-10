from django.test import TestCase, Client
from rest_framework.test import APITestCase
from rest_framework import status
from .models import User
from django.conf import settings
from django.core.management import call_command
import traceback


# This class is used to test the API endpoints
class BaseAPITestCase(APITestCase):
    client = Client()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        call_command('loaddata', 'role', 'subscription', 'tool')  # Load fixtures dynamically

    def register(self):
        """
        It creates a new user with the email and password specified in the settings.py file.
        """
        self._data = {
            "first_name": "unittest",
            "last_name": "unittest",
            "email": settings.UNIT_TEST_USER_EMAIL,
            "password": settings.UNIT_TEST_USER_PASSWORD,
            "mobile_number": "7096967474",
            "country_code": "+1",
            "confirm_password": settings.UNIT_TEST_USER_PASSWORD,
            "user_company": "test",
            "user_address": "test",
        }
        try:
            self.set_response(self.client.post(f"/api/auth/register", data=self._data, format="json"))
        except:
            traceback.print_exc()

    def login(self):
        """
        It registers a user, then logs in as that user
        """
        self._response = self.register()
        self._data = {
            "email": settings.UNIT_TEST_USER_EMAIL,
            "password": settings.UNIT_TEST_USER_PASSWORD,
        }
        self.set_response(
            self.client.post(f"/api/auth/login", data=self._data, format="json")
        )
        User.objects.filter(email="unittesting@yopmail.com").update(
            is_staff=True, is_superuser=True, role=1
        )
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self._data['data']['access']}"
        )

    def match_success_response(self):
        """
        This function checks that the status code of the response is 200 and that the response data
        matches the expected data
        """
        self.assertEqual(self._data["status_code"], status.HTTP_200_OK)
        # self.assertEqual(self._data['status'], True)

    def match_error_response(self):
        """
        It asserts that the status code is 401 and the status is False
        """
        self.assertIn(self._data["status_code"], [status.HTTP_400_BAD_REQUEST,status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])

    def set_response(self, json_obj):
        """
        The function takes a json object and sets the response to that object

        :param json_obj: The response object from the API call
        """
        self._response = json_obj
        self._data = self._response.json()

    def insert_order(self):
        """
        It creates a tool record, then creates a scan record with the tool_id and two ip addresses
        """
        self._data = {
            "tool_name": "nmap",
            "tool_cmd": "nmap -Pn -sV",
            "time_limit": 100,
            "subscription_id": 1,
        }
        self.set_response(
            self.client.post(f"{self.prefix}tool/", data=self._data, format="json")
        )
        # tool_id = self._data.get("data").get("id")
        self._data = {
            "target_ip": "20.220.195.124",
            "company_name": "unittest",
            "company_address": "unittest",
            "is_client": False,
            "client_name": "unittest",
        }
        self.set_response(
            self.client.post(f"{self.prefix}orders/", data=self._data, format="json")
        )

# It tests the authentication endpoints of the API
class AuthTest(BaseAPITestCase):
    prefix = "/api/auth/"

    def verify_token(self, token):
        """
        It sends a POST request to the endpoint `/verifyToken` with the token as the data

        :param token: The token to be verified
        """
        self._data = {"token": token}
        self.set_response(
            self.client.post(
                f"{self.prefix}verifyToken", data=self._data, format="json"
            )
        )

    def verify_refresh_token(self, token):
        """
        It sends a POST request to the endpoint `/refreshToken` with the token as the data

        :param token: The token to be verified
        """
        self._data = {"refresh": token}
        self.set_response(
            self.client.post(
                f"{self.prefix}refreshToken", data=self._data, format="json"
            )
        )

    def test_register(self):
        """
        It registers a user and then checks that the response is a success
        """
        self.register()
        self.match_success_response()

    def test_login(self):
        """
        It logs in and checks that the response is successful
        """
        self.login()
        self.match_success_response()

    def test_refresh_token(self):
        """
        It refreshes the token and then verify the response.
        """
        self.login()
        _data = {"refresh": self._data["data"]["refresh"]}
        self.set_response(
            self.client.post(f"{self.prefix}refreshToken", data=_data, format="json")
        )
        self.match_success_response()

    def test_verify_token(self):
        """
        It logs in, gets the access and refresh tokens, and then verifies them
        """
        self.login()
        access_token = self._data["data"]["access"]
        refresh_token = self._data["data"]["refresh"]
        self.verify_token(access_token)
        self.match_success_response()
        self.verify_refresh_token(refresh_token)
        self.match_success_response()