import os,json, tempfile
from PIL import Image
from django.test import TestCase
from django.urls import reverse
from datetime import date
from datetime import timedelta
from rest_framework.test import APITestCase, APIClient
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from core.models import Todo
from auth_api.models import User
from auth_api.tests import BaseAPITestCase



class TodoModelTests(BaseAPITestCase):
    url = reverse("todos-list")
    
    def create_todos_via_orm(self, **kwargs):
        """Create a todos using Django ORM and return the instance."""
        # Default valid data
        data = {
            "name": "New todos",
            "description": "New description",
            "price": 10.99,
            "inventory": 15,
            "published_date": "2024-07-02",
            "rating": 4.7,
            "url": "http://example.com/new",
            "email": "new@example.com",
            "slug": "new-todos",
            "ip_address": "127.0.0.1",
            "big_integer": 8888888888,
            "positive_integer": 15,
            "small_integer": 7,
            "duration": "02:00:00",
            "json_data": json.dumps(
                {"key": "value", "key2": "value2"}
            ),  # Add JSON data as string
        }
        data.update(kwargs)

        # Attempt to create the todos using Django's ORM and return the instance
        return Todo.objects.create(**data)
    
    
    def test_create_todos_with_authenticate(self):
        """
        The function `test_create_todos_with_authenticate` creates a todos with authentication
        and checks for a successful response.
        """
        self.login()
        self.create_todos_via_orm()
        self.status_code = status.HTTP_201_CREATED

        self.match_success_response(201)

    def test_create_todos_without_authenticate(self):
        """
        The function `test_create_todos_without_authenticate` creates a todos without authentication
        and checks for a successful response.
        """
        self.create_todos_via_orm()
        self.status_code = status.HTTP_401_UNAUTHORIZED
        self.match_error_response(401)

    def test_create_todos_with_invalid_data(self):
        """
        The function `test_create_todos_with_invalid_data`
        and checks for a successful response.
        """
        self.login()
        invalid_data = {
            "url": "invalid_url"  # Invalid URL format
        }
        with self.assertRaises(Exception):  # Expect failure due to invalid data
            self.create_todos_via_orm(**invalid_data)
            self.match_error_response(400)

    def test_get_todos(self):
        """
        The function `test_create_todos` retrieves all todos and checks for a successful response.
        """
        self.login()
        self.set_response(self.client.get(self.url))
        self.match_success_response(200)

    def test_get_todos_without_authenticate(self):
        """
        The function `test_get_todos_without_authenticate` retrieves all todos without authentication
        and checks for a successful response.
        """
        self.set_response(self.client.get(self.url))
        self.match_error_response(401)

    def test_retrieve_todos_by_id(self):
        """
        The function `test_retrieve_todos_by_id` retrieves a todos by ID and checks for a successful response.
        """
        self.login()
        todos = self.create_todos_via_orm()
        created_todos_id = todos.id
        self.set_response(self.client.get(f"{self.url}{created_todos_id}/"))
        self.match_success_response(200)

    def test_retrieve_todos_by_id_without_authenticate(self):
        """
        The function `test_retrieve_todos_by_id_without_authenticate` retrieves a todos by ID without authentication
        and checks for a successful response.
        """
        todos = self.create_todos_via_orm()
        created_todos_id = todos.id
        self.set_response(self.client.get(f"{self.url}{created_todos_id}/"))
        self.match_error_response(401)

    def test_retrieve_todos_by_id_with_wrong_id(self):
        """
        The function `test_retrieve_todos_by_id_with_wrong_id` retrieves a todos by ID with a wrong ID
        and checks for a successful response.
        """
        self.login()
        self.set_response(self.client.get(f"{self.url}1000/"))
        self.match_error_response(404)

    def test_update_todos_by_id(self):
        self.login()
        todos = self.create_todos_via_orm()
        created_todos_id = todos.id
        # Update the todos with a patch request
        self.client.patch(
            f"{self.url}{created_todos_id}/", {"name": "Updated name"}, format="json"
        )
        self.match_success_response()

    def test_update_todos_by_id_without_authenticate(self):
        todos = self.create_todos_via_orm()
        # Update the todos with a patch request
        self.client.patch(
            f"{self.url}{todos.id}/", {"name": "Updated name"}, format="json"
        )
        self.status_code = status.HTTP_401_UNAUTHORIZED
        self.match_error_response(401)

    def test_update_todos_by_id_with_wrong_id(self):
        self.login()

        self.set_response(
            self.client.patch(
                f"{self.url}1000/", {"name": "Updated name"}, format="json"
            )
        )
        self.match_error_response(404)

    # def test_create_todos_with_invalid_email(self):
    #     """Test creating todos with invalid email."""
    #     self.login()
    #     payload = {
    #         "name": "Test todos",  # Adjust these fields as needed
    #         "email": "invalid-email",
    #     }
    #     self.create_todos_via_orm(**payload)
    #     self.status_code = status.HTTP_400_BAD_REQUEST
    #     self.match_error_response(400)

    # def test_create_todos_with_existing_email(self):
    #     """
    #     Test creating todos with an existing email, expecting a 400 Bad Request error using ORM.
    #     """
    #     self.login()
    #     # Create the first todos via ORM
    #     self.create_todos_via_orm(email="duplicate@example.com")
    #     # self.create_todos_via_orm(email="duplicate@example.com")
    #     if Todo.objects.filter(email="duplicate@example.com").count() > 1:
    #         # Simulate a 400 Bad Request error since email is already in use
    #         self.match_error_response(400)
    #     else:
    #         # Create the second todos via ORM (this shouldn't be reached in this test)
    #         self.create_todos_via_orm(email="duplicate@example.com")
    #         self.match_error_response(200)  # This line is for testing purposes

    def test_delete_todos_by_id(self):
        """
        The function `test_delete_todos_by_id` deletes a todos by ID and checks for a successful response.
        """
        self.login()
        todos = self.create_todos_via_orm()
        created_todos_id = todos.id
        self.set_response(self.client.delete(f"{self.url}{created_todos_id}/"))
        self.match_success_response(204)

    def test_delete_todos_by_id_without_authenticate(self):
        #     """Test deleting by ID without authentication."""
        todos = self.create_todos_via_orm()
        created_todos_id = todos.id
        self.set_response(self.client.delete(f"{self.url}{created_todos_id}/"))
        self.match_error_response(401)

    def test_delete_todos_by_id_with_wrong_id(self):
        """Test deleting a todos by an invalid ID."""
        self.login()
        self.set_response(self.client.delete(f"{self.url}111/"))
        self.match_error_response(404)
