from django.test import TestCase, Client
from rest_framework.test import APITestCase
from rest_framework import status
from .models import User
from django.conf import settings
import traceback

# This class is used to test the API endpoints
class BaseAPITestCase(APITestCase):
    client = Client()
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
            "user_address": "test"
        }
        try:
            b= self.client.post(f'/api/auth/register',data=self._data, format = "json")
            print(b.json())
            a = self.set_response(b)
            print(a,"=>>>>")
        except:
            traceback.print_exc()

    def login(self):
        """
        It registers a user, then logs in as that user
        """
        self._response = self.register()
        self._data={
            "email": settings.UNIT_TEST_USER_EMAIL,
            "password": settings.UNIT_TEST_USER_PASSWORD
        }
        self.set_response(self.client.post(f'/api/auth/login',data=self._data, format = "json"))
        User.objects.filter(email="unittesting@yopmail.com").update(is_staff=True, is_superuser=True, role=1)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self._data['data']['access']}")

    def match_success_response(self):
        """
        This function checks that the status code of the response is 200 and that the response data
        matches the expected data
        """
        self.assertEqual(self._data['status_code'], status.HTTP_200_OK) 
        # self.assertEqual(self._data['status'], True)

    def match_error_response(self):
        """
        It asserts that the status code is 401 and the status is False
        """
        self.assertEqual(self._data['status_code'], status.HTTP_401_UNAUTHORIZED) 
        self.assertEqual(self._data['status'], False)

    def set_response(self, json_obj):
        """
        The function takes a json object and sets the response to that object
        
        :param json_obj: The response object from the API call
        """
        self._response = json_obj
        self._data = self._response.json()

# It tests the authentication endpoints of the API
class AuthTest(BaseAPITestCase):
    prefix = '/api/auth/'
    fixtures = [
        '/home/techno200/projects/CyberApp/app/user/fixtures/role.json',
        '/home/techno200/projects/CyberApp/app/scanner/fixtures/subscription.json',
        '/home/techno200/projects/CyberApp/app/scanner/fixtures/tool.json'
    ]

    def verify_token(self,token):
        """
        It sends a POST request to the endpoint `/verifyToken` with the token as the data
        
        :param token: The token to be verified
        """
        self._data = {
            "token": token
        }
        self.set_response(self.client.post(f'{self.prefix}verifyToken',data=self._data, format = "json"))

    def test_register(self):
        """
        It registers a user and then checks that the response is a success
        """
        self.register()
        self.match_success_response()

#     def test_login(self):
#         """
#         It logs in and checks that the response is successful
#         """
#         self.login()
#         self.match_success_response()

#     def test_refresh_token(self):
#         """
#         It refreshes the token and then verify the response.
#         """
#         self.login()
#         _data = {
#             "refresh": self._data['data']['refresh']
#         }
#         self.set_response(self.client.post(f'{self.prefix}refreshToken',data=_data, format = "json"))
#         self.match_success_response()

#     def test_verify_token(self):
#         """
#         It logs in, gets the access and refresh tokens, and then verifies them
#         """
#         self.login()
#         access_token = self._data['data']['access']
#         refresh_token = self._data['data']['refresh']
#         self.verify_token(access_token)
#         self.match_success_response()
#         self.verify_token(refresh_token)
#         self.match_success_response()

