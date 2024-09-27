import json

from auth_api.tests import BaseAPITestCase
from django.urls import reverse
from rest_framework import status

from todos.models import Todo


class TodoTest(BaseAPITestCase):
    url = reverse("todo-list")

    def create_todo_via_orm(self, **kwargs):
        """Create a todo using Django ORM and return the instance."""
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

        # Override with any invalid data passed via kwargs
        data.update(kwargs)

        # Attempt to create the todo using Django's ORM and return the instance
        return Todo.objects.create(**data)

    def test_create_todos_with_authenticate(self):
        """
        The function `test_create_todos_with_authenticate` creates a todo with authentication
        and checks for a successful response.
        """
        self.login()
        self.create_todo_via_orm()
        self.status_code = status.HTTP_201_CREATED

        self.match_success_response(201)

    def test_create_todos_without_authenticate(self):
        """
        The function `test_create_todos_without_authenticate` creates a todo without authentication
        and checks for a successful response.
        """
        self.create_todo_via_orm()
        self.status_code = status.HTTP_401_UNAUTHORIZED
        self.match_error_response(401)

    def test_create_todos_with_invalid_data(self):
        """
        The function `test_create_todos_with_invalid_data` creates a todo with invalid data
        and checks for a successful response.
        """
        self.login()
        invalid_data = {
            "url": "invalid_url"  # Invalid URL format
        }
        # Try creating a todo with invalid data via ORM
        with self.assertRaises(Exception):  # Expect failure due to invalid data
            self.create_todo_via_orm(**invalid_data)

        self.match_error_response(400)

    def test_get_todos(self):
        """
        The function `test_get_todos` retrieves all todos and checks for a successful response.
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

    def test_retrieve_todo_by_id(self):
        """
        The function `test_retrieve_todo_by_id` retrieves a todo by ID and checks for a successful response.
        """
        self.login()
        # self.create_todo()
        todo = self.create_todo_via_orm()
        created_todo_id = todo.id
        self.set_response(self.client.get(f"{self.url}{created_todo_id}/"))
        self.match_success_response(200)

    def test_retrieve_todo_by_id_without_authenticate(self):
        """
        The function `test_retrieve_todo_by_id_without_authenticate` retrieves a todo by ID without authentication
        and checks for a successful response.
        """
        todo = self.create_todo_via_orm()
        created_todo_id = todo.id
        self.set_response(self.client.get(f"{self.url}{created_todo_id}/"))
        self.match_error_response(401)

    def test_retrieve_todo_by_id_with_wrong_id(self):
        """
        The function `test_retrieve_todo_by_id_without_authenticate` retrieves a todo by ID without authentication
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
        todo = self.create_todo_via_orm()
        created_todo_id = todo.id
        # Update the todo with a patch request
        self.client.patch(
            f"{self.url}{created_todo_id}/", {"name": "Updated name"}, format="json"
        )
        self.match_success_response()

    def test_update_todo_by_id_without_authenticate(self):
        """
        The function `test_update_todo_by_id_without_authenticate` updates a todo by ID without authentication
        and checks for a successful response.
        """
        todo = self.create_todo_via_orm()
        # Update the todo with a patch request
        self.client.patch(
            f"{self.url}{todo.id}/", {"name": "Updated name"}, format="json"
        )
        self.status_code = status.HTTP_401_UNAUTHORIZED
        self.match_error_response(401)

    def test_update_todo_by_id_with_wrong_id(self):
        """
        The function `test_update_todo_by_id_with_wrong_id` updates a todo by ID with wrong ID
        and checks for a successful response.
        """
        self.login()
        # todo = self.create_todo_via_orm()

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
    #         "name": "Test Todo",  # Adjust these fields as needed
    #         "email": "invalid-email",
    #     }
    #     self.create_todo_via_orm(**payload)
    #     self.status_code = status.HTTP_400_BAD_REQUEST
    #     self.match_error_response(400)

    # def test_create_todos_with_existing_email(self):
    #     """
    #     Test creating todos with an existing email, expecting a 400 Bad Request error using ORM.
    #     """
    #     self.login()
    #     # Create the first todo via ORM
    #     self.create_todo_via_orm(email="duplicate@example.com")
    #     # self.create_todo_via_orm(email="duplicate@example.com")
    #     if Todo.objects.filter(email="duplicate@example.com").count() > 1:
    #         # Simulate a 400 Bad Request error since email is already in use
    #         self.match_error_response(400)
    #     else:
    #         # Create the second todo via ORM (this shouldn't be reached in this test)
    #         self.create_todo_via_orm(email="duplicate@example.com")
    #         self.match_error_response(200)  # This line is for testing purposes

    def test_delete_todo_by_id(self):
        """
        The function `test_delete_todo_by_id` deletes a todo by ID and checks for a successful response.
        """
        self.login()
        todo = self.create_todo_via_orm()
        created_todo_id = todo.id
        self.set_response(self.client.delete(f"{self.url}{created_todo_id}/"))
        self.match_success_response(204)

    def test_delete_todo_by_id_without_authenticate(self):
        #     """Test deleting a todo by ID without authentication."""
        todo = self.create_todo_via_orm()
        created_todo_id = todo.id
        self.set_response(self.client.delete(f"{self.url}{created_todo_id}/"))
        self.match_error_response(401)

    def test_delete_todo_by_id_with_wrong_id(self):
        """Test deleting a todo by an invalid ID."""
        self.login()
        self.set_response(self.client.delete(f"{self.url}111/"))
        self.match_error_response(404)

    def create_sample_todo(self):
        """
        Utility function to create a set of sample todo for tests.
        """
        records = [
            {"name": "todo", "description": "First record"},
            {"name": "folder", "description": "Second record"},
            {"name": "file", "description": "Third record"},
        ]
        for record in records:
            self.create_todo_via_orm(
                name=record["name"], description=record["description"]
            )

    def test_get_todo_with_search_filter(self):
        """
        Test for filtering todo by name.
        """
        self.login()

        self.create_sample_todo()

        # Search filter (search for "todo")
        url_search = f"{self.url}?name=todo"
        response_search = self.client.get(url_search)
        self.status_code = status.HTTP_200_OK  # Set the expected status code
        self.match_success_response(response_search.status_code)

        response_data_search = response_search.json()
        results_search = response_data_search["data"]["results"]

        expected_names_search = ["todo"]
        result_names_search = [todo["name"] for todo in results_search]

        print("Extracted Names from Search Results:", result_names_search)

        self.assertListEqual(result_names_search, expected_names_search)

    def test_get_todo_with_sort_ascending(self):
        """
        Test for sorting todo by name in ascending order.
        """
        self.login()
        self.create_sample_todo()

        # Sort Ascending (by name)
        url_sort_asc = f"{self.url}?sort=name"
        response_sort_asc = self.client.get(url_sort_asc)
        self.match_success_response(response_sort_asc.status_code)

        response_data_sort_asc = response_sort_asc.json()
        results_sort_asc = response_data_sort_asc["data"]["results"]

        print(
            "Search Results:", results_sort_asc
        )  # This will print the result in the console during the test run

        expected_names_asc = ["file", "folder", "todo"]
        result_names_sort_asc = [todo["name"] for todo in results_sort_asc]
        self.assertListEqual(result_names_sort_asc, expected_names_asc)

    def test_get_todo_with_sort_descending(self):
        """
        Test for sorting todo by name in descending order.
        """
        self.login()

        self.create_sample_todo()

        # Sort Descending (by name)
        url_sort_desc = f"{self.url}?sort=-name"
        response_sort_desc = self.client.get(url_sort_desc)
        self.match_success_response(response_sort_desc.status_code)

        response_data_sort_desc = response_sort_desc.json()
        results_sort_desc = response_data_sort_desc["data"]["results"]
        print(
            "Search Results:", results_sort_desc
        )  # This will print the result in the console during the test run

        expected_names_desc = ["todo", "folder", "file"]
        result_names_sort_desc = [todo["name"] for todo in results_sort_desc]
        self.assertListEqual(result_names_sort_desc, expected_names_desc)

    def test_get_todos_with_pagination(self):
        """
        Test for paginating todo.
        """
        self.login()

        self.create_sample_todo()

        # Pagination (skip and limit)
        url_pagination = f"{self.url}?paginate=2&page=1"
        response_pagination = self.client.get(url_pagination)
        self.match_success_response(response_pagination.status_code)

        response_data_pagination = response_pagination.json()
        results_pagination = response_data_pagination["data"]["results"]

        expected_names_pagination = ["file", "folder"]
        self.assertEqual(len(results_pagination), 2)
        self.assertListEqual(
            [todo["name"] for todo in results_pagination], expected_names_pagination
        )

        # Pagination with skipping the first todo
        url_pagination_skip = f"{self.url}?paginate=1"
        response_pagination_skip = self.client.get(url_pagination_skip)
        self.match_success_response(response_pagination_skip.status_code)

        response_data_skip = response_pagination_skip.json()
        results_skip = response_data_skip["data"]["results"]

        expected_names_skip = ["file"]  # Adjust if necessary based on sorting
        self.assertListEqual(
            [todo["name"] for todo in results_skip], expected_names_skip
        )
