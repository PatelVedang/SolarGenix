from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from auth_api.models import User


class UserModelTests(TestCase):
    def setUp(self):
        # Create a superuser and set the password
        self.user = User.objects.create_superuser(
            email="testuser@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
            is_active=True,
        )

        # Authenticate the user and obtain the token
        self.client = APIClient()
        login_response = self.client.post(
            reverse("login"),
            {"email": "testuser@example.com", "password": "testpass123"},
            format="json",
        )

        # Extract access token
        self.access_token = login_response.data["data"]["access"]
        print(self.access_token, "access token")
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.access_token)

        # Set up a user instance
        self.user = User.objects.create(
            first_name="Test",
            last_name="User",
            email="info@example.com",
            password="password",
            is_active=True,
        )

    def test_create_user_authentication(self):
        url = reverse("user-list")  # Ensure this URL name matches your URL pattern

        # Flatten or serialize JSON data
        # json_data_str = json.dumps({"key": "new value"})

        data = {
            "first_name": "New",
            "last_name": "User",
            "email": "newuser@example.com",
            "password": "newpassword123",
            "is_active": True,
        }

        response = self.client.post(url, data, format="multipart")
        print(response, "response :::::::::::::")
        data = response.data.get("data", None)
        user_id = data.get("id") if data else None
        if user_id:
            User.objects.get(id=user_id)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # def test_create_user_without_authentication(self):
    #     # Authenticate the user and obtain the token
    #     self.client = APIClient()
    #     self.client.credentials()
    #     url = reverse("users")  # Ensure this URL name matches your URL pattern

    #     # Flatten or serialize JSON data
    #     json_data_str = json.dumps({"key": "new value"})

    #     data = {
    #         "first_name": "New",
    #         "last_name": "User",
    #         "email": "newuser@example.com",
    #         "password": "newpassword123",
    #         "is_active": True,
    #     }

    #     response = self.client.post(url, data, format="multipart")
    #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # def test_create_user_validation(self):
    #     # Authenticate the user and obtain the token
    #     url = reverse("users")  # Ensure this URL name matches your URL pattern

    #     # Flatten or serialize JSON data
    #     json_data_str = json.dumps({"key": "new value"})

    #     data = {
    #         "first_name": 123,  # pass int value instead of str
    #         "last_name": "User",
    #         "email": "newuser@example.com",
    #         "password": "newpassword123",
    #         "is_active": True,
    #     }

    #     response = self.client.post(url, data, format="multipart")
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # def test_read_user_authentication(self):
    #     url = reverse(
    #         "user-detail", args=[self.user.id]
    #     )  # Ensure this URL name matches your URL pattern

    #     response = self.client.get(url, format="json")
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(response.data["data"]["first_name"], self.user.first_name)

    # def test_read_user_without_authentication(self):
    #     # Authenticate the user and obtain the token
    #     self.client = APIClient()
    #     self.client.credentials()

    #     url = reverse(
    #         "user-detail", args=[self.user.id]
    #     )  # Ensure this URL name matches your URL pattern

    #     response = self.client.get(url, format="json")
    #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # def test_read_user_with_not_exists_id(self):
    #     url = reverse(
    #         "user-detail", args=[123456789]
    #     )  # Ensure this URL name matches your URL pattern

    #     response = self.client.get(url, format="json")
    #     self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # def test_update_user_authentication(self):
    #     url = reverse(
    #         "user-detail", args=[self.user.id]
    #     )  # Ensure this URL name matches your URL pattern

    #     updated_data = {
    #         "first_name": "Updated",
    #         "last_name": "User",
    #         "email": "updated@example.com",
    #         "password": "updatedpassword123",
    #         "is_active": False,
    #     }

    #     response = self.client.patch(url, updated_data, format="multipart")
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(
    #         response.data["data"]["first_name"], updated_data["first_name"]
    #     )

    # def test_update_user_without_authentication(self):
    #     # Authenticate the user and obtain the token
    #     self.client = APIClient()
    #     self.client.credentials()

    #     url = reverse(
    #         "user-detail", args=[self.user.id]
    #     )  # Ensure this URL name matches your URL pattern

    #     updated_data = {
    #         "first_name": "Updated",
    #         "last_name": "User",
    #         "email": "updated@example.com",
    #         "password": "updatedpassword123",
    #         "is_active": False,
    #     }

    #     response = self.client.patch(url, updated_data, format="multipart")
    #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # def test_update_user_validation(self):
    #     url = reverse(
    #         "user-detail", args=[self.user.id]
    #     )  # Ensure this URL name matches your URL pattern

    #     updated_data = {"email": "not-an-email"}

    #     response = self.client.patch(url, updated_data, format="json")
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # def test_update_user_with_not_exists_id(self):
    #     url = reverse(
    #         "user-detail", args=[0]
    #     )  # Ensure this URL name matches your URL pattern

    #     updated_data = {
    #         "first_name": "Updated",
    #         "last_name": "User",
    #         "email": "updated@example.com",
    #         "password": "updatedpassword123",
    #         "is_active": False,
    #     }

    #     response = self.client.patch(url, updated_data, format="multipart")
    #     self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # def test_partial_update_user_authenticated(self):
    #     url = reverse(
    #         "user-detail", args=[self.user.id]
    #     )  # Ensure this URL name matches your URL pattern

    #     updated_data = {"name": "Partially Updated User"}

    #     response = self.client.patch(url, updated_data, format="json")
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(response.data["data"]["name"], updated_data["name"])

    # def test_partial_update_user_without_authentication(self):
    #     # Authenticate the user and obtain the token
    #     self.client = APIClient()
    #     self.client.credentials()

    #     url = reverse(
    #         "user-detail", args=[self.user.id]
    #     )  # Ensure this URL name matches your URL pattern

    #     updated_data = {"name": "Partially Updated User"}

    #     response = self.client.patch(url, updated_data, format="json")
    #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # def test_partial_update_user_validation(self):
    #     url = reverse(
    #         "user-detail", args=[self.user.id]
    #     )  # Ensure this URL name matches your URL pattern

    #     updated_data = {"url": "Partially Updated User"}

    #     response = self.client.patch(url, updated_data, format="json")
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # def test_delete_user_authenticated(self):
    #     url = reverse(
    #         "user-detail", args=[self.user.id]
    #     )  # Ensure this URL name matches your URL pattern

    #     response = self.client.delete(url, format="json")
    #     self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    #     self.assertFalse(User.objects.filter(id=self.user.id).exists())

    # def test_delete_user_without_authentication(self):
    #     # Authenticate the user and obtain the token
    #     self.client = APIClient()
    #     self.client.credentials()

    #     url = reverse(
    #         "user-detail", args=[self.user.id]
    #     )  # Ensure this URL name matches your URL pattern

    #     response = self.client.delete(url, format="json")
    #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # def test_delete_user_not_exists_id(self):
    #     url = reverse(
    #         "user-detail", args=[0]
    #     )  # Ensure this URL name matches your URL pattern

    #     response = self.client.delete(url, format="json")
    #     self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # def test_list_all_user(self):
    #     self.access_token = ""
    #     url = reverse("users")
    #     response = self.client.get(url, format="json")
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
