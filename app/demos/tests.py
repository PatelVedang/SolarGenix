import os
import json
import tempfile
from PIL import Image
from django.test import TestCase
from django.urls import reverse
from datetime import date
from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from .models import Demo
from auth_api.models import User


class DemoModelTests(TestCase):
    # def setUp(self):
    #     self.demo_instance = Demo.objects.create(
    #         name="Test Name",
    #         description="Test description",
    #         price=9.99,
    #         inventory=100,
    #         available=True,
    #         published_date="2024-01-01",
    #         rating=4.5,
    #         url="https://example.com",
    #         email="test@example.com",
    #         slug="test-name",
    #         ip_address="127.0.0.1",
    #         big_integer=9999999999,
    #         positive_integer=123,
    #         small_integer=12,
    #         duration=timedelta(days=1),
    #         json_data={"key": "value"}
    #     )

    # def test_demo_creation(self):
    #     self.assertIsInstance(self.demo_instance, Demo)
    #     self.assertEqual(self.demo_instance.__str__(), self.demo_instance.name)
    def setUp(self):
        # Create a user and set the password
        self.user = User.objects.create_superuser(
            email="testuser@example.com",
            name="Test User",
            password="testpass123",
            tc=True,
        )
        self.user.is_active = True
        self.user.save()

        # Authenticate the user and obtain the token
        self.client = APIClient()
        login_response = self.client.post(
            reverse("login"),
            {"email": "testuser@example.com", "password": "testpass123"},
            format="json",
        )

        # Extract access token
        self.access_token = login_response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.access_token)

        # Create a temporary image for testing
        self.image = self.generate_test_image()
        # Create a temporary file for testing
        self.file, self.file_path = self.generate_test_file()

        # Set up a demo instance
        self.demo = Demo.objects.create(
            name="Test Name",
            description="Test description",
            price=9.99,
            inventory=10,
            published_date=date(2024, 7, 1),
            rating=4.5,
            url="http://example.com",
            email="info@example.com",
            slug="test-demo",
            ip_address="127.0.0.1",
            big_integer=9999999999,
            positive_integer=10,
            small_integer=5,
            duration="01:00:00",
            json_data={"key": "value"},
            image=self.image,
            file=self.file,
        )

    def generate_test_image(self):
        # Create a temporary image file
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_image:
            image = Image.new("RGB", (100, 100), color=(255, 0, 0))
            image.save(temp_image, format="PNG")
            temp_image.seek(0)
            return SimpleUploadedFile(
                temp_image.name, temp_image.read(), content_type="image/png"
            )

    def generate_test_file(self):
        # Create a temporary file
        file_content = b"This is a test file."
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.write(file_content)
        temp_file.flush()
        temp_file.seek(0)  # Go back to the start of the file for reading
        return SimpleUploadedFile(
            temp_file.name, temp_file.read(), content_type="text/plain"
        ), temp_file.name

    def test_create_demo_authentication(self):
        url = reverse("demo-list")  # Ensure this URL name matches your URL pattern

        # Flatten or serialize JSON data
        json_data_str = json.dumps({"key": "new value"})

        sample_image = self.generate_test_image()
        test_file = self.generate_test_file()
        data = {
            "name": "New demos",
            "description": "New description",
            "price": 10.99,
            "inventory": 15,
            "published_date": "2024-07-02",
            "rating": 4.7,
            "url": "http://example.com/new",
            "email": "new@example.com",
            "slug": "new-demo",
            "ip_address": "127.0.0.1",
            "big_integer": 8888888888,
            "positive_integer": 15,
            "small_integer": 7,
            "duration": "02:00:00",
            "json_data": json_data_str,  # Pass JSON data as string
            "image": sample_image,  # Add image here
            "file": test_file,  # Add file here
        }

        response = self.client.post(url, data, format="multipart")
        data = response.data.get("data", None)
        demo_id = data.get("id") if data else None
        if demo_id:
            demo_instance = Demo.objects.get(id=demo_id)
            if demo_instance.image:
                demo_instance.image.delete(save=False)
            if demo_instance.file:
                demo_instance.file.delete(save=False)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_demo_without_authentication(self):
        # Authenticate the user and obtain the token
        self.client = APIClient()
        self.client.credentials()
        url = reverse("demo-list")  # Ensure this URL name matches your URL pattern

        # Flatten or serialize JSON data
        json_data_str = json.dumps({"key": "new value"})

        sample_image = self.generate_test_image()
        test_file = self.generate_test_file()
        data = {
            "name": "New Demo",
            "description": "New description",
            "price": 10.99,
            "inventory": 15,
            "published_date": "2024-07-02",
            "rating": 4.7,
            "url": "http://example.com/new",
            "email": "new@example.com",
            "slug": "new-demo",
            "ip_address": "127.0.0.1",
            "big_integer": 8888888888,
            "positive_integer": 15,
            "small_integer": 7,
            "duration": "02:00:00",
            "json_data": json_data_str,  # Pass JSON data as string
            "image": sample_image,  # Add image here
            "file": test_file,  # Add file here
        }

        response = self.client.post(url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_demo_validation(self):
        # Authenticate the user and obtain the token
        url = reverse("demo-list")  # Ensure this URL name matches your URL pattern

        # Flatten or serialize JSON data
        json_data_str = json.dumps({"key": "new value"})

        sample_image = self.generate_test_image()
        test_file = self.generate_test_file()
        data = {
            "name": 123,  # pass int value instead of str
            "description": "New description",
            "price": 10.99,
            "inventory": 15,
            "published_date": "2024-07-02",
            "rating": "4.7",
            "url": "example.com/new",  # pass wrong field value
            "email": "new",
            "slug": "new-demo",
            "ip_address": "127.0.0.1",
            "big_integer": 8888888888,
            "positive_integer": 15,
            "small_integer": 7,
            "duration": "02:00:00",
            "json_data": json_data_str,  # Pass JSON data as string
            "image": sample_image,  # Add image here
            "file": test_file,  # Add file here
        }

        response = self.client.post(url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_read_demo_authentication(self):
        url = reverse(
            "demo-detail", args=[self.demo.id]
        )  # Ensure this URL name matches your URL pattern

        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["name"], self.demo.name)

    def test_read_demo_without_authentication(self):
        # Authenticate the user and obtain the token
        self.client = APIClient()
        self.client.credentials()

        url = reverse(
            "demo-detail", args=[self.demo.id]
        )  # Ensure this URL name matches your URL pattern

        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # self.assertEqual(response.data['data']['name'], self.demo.name)

    def test_read_demo_with_not_exists_id(self):
        url = reverse(
            "demo-detail", args=[1231465]
        )  # Ensure this URL name matches your URL pattern

        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # self.assertEqual(response.data['data']['name'], self.demo.name)

    def test_update_demo_authentication(self):
        url = reverse(
            "demo-detail", args=[self.demo.id]
        )  # Ensure this URL name matches your URL pattern

        updated_data = {
            "name": "Updated demo",
            "description": "Updated description",
            "price": 11.99,
            "inventory": 20,
            "published_date": "2024-07-03",
            "rating": 4.9,
            "url": "http://example.com/updated",
            "email": "updated@example.com",
            "slug": "updated-demo",
            "ip_address": "127.0.0.2",
            "big_integer": 7777777777,
            "positive_integer": 20,
            "small_integer": 10,
            "duration": "03:00:00",
            "json_data": json.dumps(
                {"key": "updated value"}
            ),  # Pass JSON data as string
            "image": self.generate_test_image(),  # Add updated image here
            "file": self.generate_test_file(),  # Add updated file here
        }

        response = self.client.patch(url, updated_data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["name"], updated_data["name"])

    def test_update_demo_without_authentication(self):
        # Authenticate the user and obtain the token
        self.client = APIClient()
        self.client.credentials()

        url = reverse(
            "demo-detail", args=[self.demo.id]
        )  # Ensure this URL name matches your URL pattern

        updated_data = {
            "name": "Updated Demo",
            "description": "Updated description",
            "price": 11.99,
            "inventory": 20,
            "published_date": "2024-07-03",
            "rating": 4.9,
            "url": "http://example.com/updated",
            "email": "updated@example.com",
            "slug": "updated-demo",
            "ip_address": "127.0.0.2",
            "big_integer": 7777777777,
            "positive_integer": 20,
            "small_integer": 10,
            "duration": "03:00:00",
            "json_data": json.dumps(
                {"key": "updated value"}
            ),  # Pass JSON data as string
            "image": self.generate_test_image(),  # Add updated image here
            "file": self.generate_test_file(),  # Add updated file here
        }

        response = self.client.patch(url, updated_data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_demo_validation(self):
        url = reverse(
            "demo-detail", args=[self.demo.id]
        )  # Ensure this URL name matches your URL pattern

        updated_data = {"url": "worng value"}

        response = self.client.patch(url, updated_data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_demo_with_not_exists_id(self):
        url = reverse(
            "demo-detail", args=[0]
        )  # Ensure this URL name matches your URL pattern

        updated_data = {
            "name": "Updated Demo",
            "description": "Updated description",
            "price": 11.99,
            "inventory": 20,
            "published_date": "2024-07-03",
            "rating": 4.9,
            "url": "http://example.com/updated",
            "email": "updated@example.com",
            "slug": "updated-demo",
            "ip_address": "127.0.0.2",
            "big_integer": 7777777777,
            "positive_integer": 20,
            "small_integer": 10,
            "duration": "03:00:00",
            "json_data": json.dumps(
                {"key": "updated value"}
            ),  # Pass JSON data as string
            "image": self.generate_test_image(),  # Add updated image here
            "file": self.generate_test_file(),  # Add updated file here
        }

        response = self.client.patch(url, updated_data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_partial_update_demo_authenticated(self):
        url = reverse(
            "demo-detail", args=[self.demo.id]
        )  # Ensure this URL name matches your URL pattern

        updated_data = {"name": "Partially Updated Demo"}

        response = self.client.patch(url, updated_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["name"], updated_data["name"])

    def test_partial_update_demo_without_authentication(self):
        # Authenticate the user and obtain the token
        self.client = APIClient()
        self.client.credentials()

        url = reverse(
            "demo-detail", args=[self.demo.id]
        )  # Ensure this URL name matches your URL pattern

        updated_data = {"name": "Partially Updated Demo"}

        response = self.client.patch(url, updated_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_partial_update_demo_validation(self):
        url = reverse(
            "demo-detail", args=[self.demo.id]
        )  # Ensure this URL name matches your URL pattern

        updated_data = {"url": "Partially Updated Demo"}

        response = self.client.patch(url, updated_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_demo_authenticated(self):
        url = reverse(
            "demo-detail", args=[self.demo.id]
        )  # Ensure this URL name matches your URL pattern

        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Demo.objects.filter(id=self.demo.id).exists())

    def test_delete_demo_without_authentication(self):
        # Authenticate the user and obtain the token
        self.client = APIClient()
        self.client.credentials()

        url = reverse(
            "demo-detail", args=[self.demo.id]
        )  # Ensure this URL name matches your URL pattern

        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_demo_not_exists_id(self):
        url = reverse(
            "demo-detail", args=[0]
        )  # Ensure this URL name matches your URL pattern

        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_all_demo(self):
        self.access_token = ""
        url = reverse("demo-list")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def tearDown(self):
        # Delete temporary files after the test
        self.demo.image.delete(
            save=False
        )  # Delete the image file if it was saved to media
        self.demo.file.delete(save=False)  # Delete the file if it was saved to media
        if os.path.exists(self.file_path):
            os.remove(self.file_path)
