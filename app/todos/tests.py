from django.urls import reverse
from .models import Todo
from auth_api.tests import BaseAPITestCase
import json


class TodoTest(BaseAPITestCase):
    url = reverse("todo-list")

    def temp_payload(self, **kwargs):
        if not kwargs:
            json_data = {
                "key": "value",
                "key2": "value2",
            }
            json_data_str = json.dumps(json_data)
            test_file = self.generate_text_file()
            sample_image = self.generate_image()
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
                "json_data": json_data_str,  # Pass JSON data as string
                "image": sample_image,  # Add image here
                "file": test_file,  # Add file here
            }
        else:
            data = kwargs
        return {**data}

    def create_todo(self, **kwargs):
        self._data = self.temp_payload(**kwargs)
        self.set_response(self.client.post(self.url, self._data, format="multipart"))

    def test_create_todos_with_authenticate(self):
        """
        The function `test_create_todos_with_authenticate` creates a todo with authentication
        and checks for a successful response.
        """
        self.login()
        self.create_todo()
        self.match_success_response(201)

    def test_create_todos_without_authenticate(self):
        """
        The function `test_create_todos_without_authenticate` creates a todo without authentication
        and checks for a successful response.
        """
        self.create_todo()
        self.match_error_response(401)

    def test_create_todos_with_invalid_data(self):
        """
        The function `test_create_todos_with_invalid_data` creates a todo with invalid data
        and checks for a successful response.
        """
        self.login()
        kwargs = self.temp_payload()
        kwargs["url"] = "test"
        self.create_todo(**kwargs)
        self.match_error_response(400)

    def test_get_todos(self):
        """
        The function `test_get_todos` retrieves all todos and checks for a successful response.
        """
        self.login()
        self.set_response(self.client.get(self.url))
        self.match_success_response()

    def test_get_todos_without_authenticate(self):
        """
        The function `test_get_todos_without_authenticate` retrieves all todos without authentication
        and checks for a successful response.
        """
        self.set_response(self.client.get(self.url))
        self.match_error_response(401)

    def test_retrive_todo_by_id(self):
        """
        The function `test_retrive_todo_by_id` retrieves a todo by ID and checks for a successful response.
        """
        self.login()
        self.create_todo()
        self.set_response(self.client.get(f"{self.url}1/"))
        self.match_success_response()

    def test_retrive_todo_by_id_without_authenticate(self):
        """
        The function `test_retrive_todo_by_id_without_authenticate` retrieves a todo by ID without authentication
        and checks for a successful response.
        """
        self.create_todo()
        self.set_response(self.client.get(f"{self.url}1/"))
        self.match_error_response(401)

    def test_retrive_todo_by_id_with_wrong_id(self):
        """
        The function `test_retrive_todo_by_id_without_authenticate` retrieves a todo by ID without authentication
        and checks for a successful response.
        """
        self.login()
        self.set_response(self.client.get(f"{self.url}1000/"))
        self.match_error_response(404)

    def test_update_todo_by_id(self):
        """
        The function `test_update_todo_by_id` updates a todo by ID and checks for a successful response.
        """
        self.login()
        self.create_todo()
        self.set_response(
            self.client.patch(f"{self.url}1/", {"name": "Updated name"}, format="json")
        )
        self.match_success_response()

    def test_update_todo_by_id_without_authenticate(self):
        """
        The function `test_update_todo_by_id_without_authenticate` updates a todo by ID without authentication
        and checks for a successful response.
        """
        self.create_todo()
        self.set_response(
            self.client.patch(f"{self.url}1/", {"name": "Updated name"}, format="json")
        )
        self.match_error_response(401)

    def test_update_todo_by_id_with_wrong_id(self):
        """
        The function `test_update_todo_by_id_with_wrong_id` updates a todo by ID with wrong ID
        and checks for a successful response.
        """
        self.login()
        self.set_response(
            self.client.patch(
                f"{self.url}1000/", {"name": "Updated name"}, format="json"
            )
        )
        self.match_error_response(404)

    def test_delete_todo_by_id(self):
        """
        The function `test_delete_todo_by_id` deletes a todo by ID and checks for a successful response.
        """
        self.login()
        self.create_todo()
        self.set_response(self.client.delete(f"{self.url}1/"))
        todo = Todo.objects.filter()
        print(todo.values())
        self.match_success_response()
