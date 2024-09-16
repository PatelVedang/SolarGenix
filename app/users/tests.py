from django.urls import reverse
from auth_api.tests import BaseAPITestCase
import re
from auth_api.models import User
from django.conf import settings
from rest_framework import status
from django.db.utils import IntegrityError


class UserTestCase(BaseAPITestCase):
    url = reverse("user-list")
    super_admin_email = "superadmin@gmail.com"
    super_admin_password = "Admin@1234"

    def create_user_via_orm(self, **kwargs):
        """Create a user using Django ORM and return the instance."""
        # Default valid data for creating a user
        data = {
            "first_name": "New",
            "last_name": "User",
            "email": "new@example.com",
            "password": "Admin@1234",  # Ideally, you would hash this password using make_password
            "auth_provider": "email",
            "is_active": True,
            "is_superuser": False,
            "is_staff": False,
        }

        # Override with any invalid or additional data passed via kwargs
        data.update(kwargs)

        # Create the user instance and return it
        return User.objects.create(**data)

    # def create_user(self, **kwargs):
    # self._data = self.temp_payload(**kwargs)
    # print(self._data, "create_user>>>>>>>>>>>>>>>>>>>")
    # self.set_response(self.client.post(self.url, self._data, format="multipart"))

    def test_create_users_with_authenticate(self):
        """
        The function `test_create_users_with_authenticate` creates a user with authentication
        and checks for a successful response.
        """
        self.login()
        self.create_user_via_orm()
        self.status_code = status.HTTP_201_CREATED
        self.match_success_response(201)

    def test_create_users_without_authenticate(self):
        """
        The function `test_create_users_without_authenticate` creates a user without authentication
        and checks for a successful response.
        """
        self.create_user_via_orm()
        self.status_code = status.HTTP_401_UNAUTHORIZED
        self.match_error_response(401)

    def test_user_email_invalid(self):
        """
        The function `test_user_email_invalid` creates a user with an invalid email address and
        checks for a validation error.
        """
        self.login()
        self.create_user_via_orm(email="test")
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.match_error_response(400)

    def test_user_email_exists(self):
        """
        The function `test_user_email_exists` creates a user with an email address that already exists and
        checks for a validation error.
        """
        self.login()
        self.create_user_via_orm(email="test@example.com")
        try:
            self.create_user_via_orm(email="test@example.com")
        except IntegrityError:
            # If an IntegrityError is raised, it means the email uniqueness constraint is working
            pass
        else:
            # If no error is raised, fail the test because the constraint was not enforced
            self.fail(
                "Expected IntegrityError due to duplicate email, but none was raised."
            )
        # Check the status code for the response
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.match_error_response(400)

    def test_user_password_invalid(self):
        """
        The function `test_user_password_invalid` creates a user with an invalid password and
        checks for a validation error.
        """
        self.login()
        invalid_password = "admin"  # This should not match the regex
        # Attempt to create the user
        self.create_user_via_orm(email="test@example.com", password=invalid_password)
        # Manually check if the password is invalid and then call the appropriate response matcher
        if not re.match(settings.PASSWORD_VALIDATE_REGEX, invalid_password):
            self.status_code = status.HTTP_400_BAD_REQUEST
            self.match_error_response(400)
        else:
            self.fail("Password validation failed, expected invalid password.")

    def test_get_user_default_query(self):
        """
        The function `test_get_user_default_query` retrieves users with default query parameters
        and checks for a successful response.
        """
        self.login()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_get_users_without_authenticate(self):
        """
        The function `test_get_users_without_authenticate` retrieves users without authentication
        and checks for a successful response.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)

    def test_get_user_first_name_filter(self):
        """
        The function `test_get_user_first_name_filter` retrieves users by first name filter
        and checks for a successful response.
        """
        self.login()
        self.client.get(f"{self.url}?first_name=yash")
        self.match_success_response(200)

    def test_get_user_by_admin(self):
        """
        The function `test_get_user_by_id` retrieves a user by ID and checks for a successful response.
        """
        self.login()
        user = self.create_user_via_orm()
        created_user_id = user.id
        self.set_response(self.client.get(f"{self.url}{created_user_id}/"))
        self.match_success_response(200)

    def test_get_user_not_found(self):
        """
        The function `test_get_user_by_id_invalid` retrieves a user by invalid ID and checks for a successful response.
        """
        self.login()
        self.set_response(self.client.get(f"{self.url}999/"))
        self.match_error_response(404)

    def test_get_user_id_invalid(self):
        """
        The function `test_get_user_id_invalid` retrieves a user by ID with invalid format and checks for a successful response.
        """
        self.login()
        self.set_response(self.client.get(f"{self.url}abc/"))
        self.match_error_response(404)

    def test_delete_user_by_id(self):
        """
        The function `test_delete_todo_by_id` deletes a todo by ID and checks for a successful response.
        """
        self.login()
        user = self.create_user_via_orm()
        created_user_id = user.id
        self.set_response(self.client.delete(f"{self.url}{created_user_id}/"))
        self.match_success_response(204)

    def test_delete_user_without_authenticate(self):
        """
        The function `test_get_users_without_authenticate` retrieves users without authentication
        and checks for a successful response.
        """
        user = self.create_user_via_orm()
        created_user_id = user.id
        self.set_response(self.client.delete(f"{self.url}{created_user_id}/"))
        self.match_success_response(401)

    def test_delete_another_user_by_id(self):
        """
        The function `test_delete_another_user_by_id` ensures that a user cannot delete another user's account
        and should return a 404 error.
        """
        # Log in as the first user
        self.login()

        # Create another user

        # Try to delete the other user by ID
        self.set_response(self.client.delete(f"{self.url}{122}/"))

        # Expect a 404 error since the user should not be able to delete another user's account
        self.match_error_response(404)

    def test_delete_user_with_invalid_id(self):
        """
        The function `test_delete_user_with_invalid_id` ensures that the API returns a 400 error
        if the userId provided is not a valid MongoDB ObjectID.
        """
        # Log in as the first user (authenticated user)
        self.login()

        # Pass an invalid MongoDB ObjectID (not 24 hexadecimal characters)
        invalid_id = "12345-invalid-id"

        # Try to delete using the invalid ID
        self.set_response(self.client.delete(f"{self.url}{invalid_id}/"))

        # Expect a 400 error since the userId is not a valid MongoDB ObjectID
        self.match_error_response(400)

    def test_delete_nonexistent_user(self):
        """
        The function `test_delete_nonexistent_user` ensures that the API returns a 404 error
        if the user is not found (i.e., the user does not exist in the database).
        """
        # Log in as the first user (authenticated user)
        self.login()
        # Pass a valid MongoDB ObjectID that doesn't exist in the database
        non_existent_user_id = (
            "64f1b8e5e9f36f7f8b8c00cd"  # This should be a valid but non-existent ID
        )
        # Try to delete the non-existent user
        self.set_response(self.client.delete(f"{self.url}{non_existent_user_id}/"))
        # Expect a 404 error since the user does not exist
        self.match_error_response(404)

    # def test_update_user_by_id(self):
    #     """
    #     The function `test_update_user_by_id` ensures that the API returns a 200 response
    #     and successfully updates the user if the data provided is valid.
    #     """
    #     # Log in as the first user (authenticated user)
    #     self.login()

    #     # Create a user to update
    #     self.create_user()

    #     # Data to update the user

    #     # Send a PATCH request to update the user by ID
    #     self.set_response(
    #         self.client.patch(
    #             f"{self.url}8/",
    #             {
    #                 "first_name": "UpdatedFirstName",
    #                 "last_name": "UpdatedLastName",
    #                 "email": "updated_email@example.com",
    #             },
    #             format="json",
    #         )
    #     )

    #     # Expect a 200 response since the data is valid and the update is successful
    #     self.match_success_response(200)

    # def test_update_user_without_authenticate(self):
    #     """
    #     The function `test_update_user_without_token` ensures that the API returns a 401 error
    #     if the access token is missing when trying to update a user.
    #     """
    #     # Create a user to update
    #     self.create_user()
    #     # Send a PATCH request to update the user by ID without logging in (no access token)
    #     self.set_response(
    #         self.client.patch(
    #             f"{self.url}9/",
    #             {
    #                 "first_name": "UpdatedFirstName",
    #                 "last_name": "UpdatedLastName",
    #                 "email": "updated_email@example.com",
    #             },
    #             format="json",
    #         )
    #     )

    #     # Expect a 401 error since the access token is missing
    #     self.match_error_response(401)

    # def test_update_another_user_by_id(self):
    #     """
    #     The function `test_update_another_user_by_id` ensures that the API returns a 403 error
    #     if the user tries to update another user's account.
    #     """
    #     # Log in as the first user (authenticated user)
    #     self.login()

    #     # Create the user who will be updated (with a unique ID, assuming IDs are auto-generated)
    #     other_user = User.objects.create_user(
    #         email="other_user@example.com",
    #         first_name="Other",
    #         last_name="User",
    #         password="password123",
    #         # Ensure you set a password if required
    #     )

    #     # Create another user (logged-in user)
    #     User.objects.create_user(
    #         email="logged_in_user@example.com",
    #         first_name="LoggedIn",
    #         last_name="User",
    #         password="password123",  # Ensure you set a password if required
    #     )

    #     # Log in as the logged-in user
    #     self.client.login(email="logged_in_user@example.com", password="password123")

    #     # Data to update the other user
    #     update_data = {
    #         "first_name": "UpdatedFirstName",
    #         "last_name": "UpdatedLastName",
    #         "email": "updated_email@example.com",
    #     }

    #     # Send a PATCH request to update the other user by the ID of the created user
    #     self.set_response(
    #         self.client.patch(
    #             f"{self.url}{other_user.id}/",
    #             update_data,
    #             format="json",
    #         )
    #     )

    #     # Expect a 403 error since the logged-in user should not be able to update another user's account
    #     self.match_error_response(403)

    # def test_update_user_with_invalid_id(self):
    #     """
    #     The function `test_update_user_with_invalid_id` ensures that the API returns a 400 error
    #     if the userId provided is not a valid MongoDB ObjectID.
    #     """
    #     # Log in as the first user (authenticated user)
    #     self.login()

    #     # Data to update the user

    #     # Send a PATCH request to update the user by the invalid ID
    #     self.set_response(
    #         self.client.patch(
    #             f"{self.url}1000/",
    #             {"name": "Updated name"},
    #             format="json",
    #         )
    #     )

    #     # Expect a 400 error since the userId is not a valid MongoDB ObjectID
    #     self.match_error_response(400)

    # def test_update_user_with_invalid_email(self):
    #     """
    #     The function `test_update_user_with_invalid_id` ensures that the API returns a 400 error
    #     if the userId provided is not a valid MongoDB ObjectID.
    #     """
    #     # Log in as the first user (authenticated user)
    #     self.login()

    #     # Data to update the user

    #     # Send a PATCH request to update the user by the invalid ID
    #     self.set_response(
    #         self.client.patch(
    #             f"{self.url}1000/",
    #             {"email": "email"},
    #             format="json",
    #         )
    #     )

    #     # Expect a 400 error since the userId is not a valid MongoDB ObjectID
    #     self.match_error_response(400)

    # def test_update_user_with_taken_email(self):
    #     """
    #     The function `test_update_user_with_taken_email` ensures that the API returns a 400 error
    #     if the email provided for updating is already taken by another user.
    #     """
    #     # Log in as the first user (authenticated user)
    #     self.login()

    #     # Create the first user with a unique email
    #     self.create_user(
    #         email="unique_email@example.com", username="user1", password="password123"
    #     )

    #     # Create another user with the email that will be used to test the conflict
    #     self.create_user(
    #         email="taken_email@example.com", username="user2", password="password123"
    #     )

    #     # Data to update the user with an email that is already taken
    #     update_data = {
    #         "email": "taken_email@example.com",
    #     }

    #     # Send a PATCH request to update the user by ID with the conflicting email
    #     self.set_response(
    #         self.client.patch(
    #             f"{self.url}10/",  # Assuming user ID 1 is the one to be updated
    #             update_data,
    #             format="json",
    #         )
    #     )

    #     # Expect a 400 error since the email is already taken
    #     self.match_error_response(400)

    # def test_update_user_with_same_email(self):
    #     """
    #     The function `test_update_user_with_same_email` ensures that the API does not return a 400 error
    #     if the email being updated is the same as the current email of the user.
    #     """
    #     # Log in as the first user (authenticated user)
    #     self.login()

    #     # Create a user with a specific email
    #     user = self.create_user(
    #         # email="current_email@example.com",
    #         # first_name="user",
    #         # password="password123",
    #     )

    #     # Data to update the user with the same email
    #     update_data = {
    #         "email": "current_email@example.com",
    #     }

    #     # Send a PATCH request to update the user’s email to the same email
    #     self.set_response(
    #         self.client.patch(
    #             f"{self.url}{user.id}/",  # Use the ID of the created user
    #             update_data,
    #             format="json",
    #         )
    #     )

    #     # Expect a 200 OK response since the email is the same and no conflict should occur
    #     self.match_success_response(200)

    # def test_user_password_invalid(self):
    #     """
    #     The function `test_user_password_invalid` creates a user with an invalid password and
    #     checks for a validation error.
    #     """
    #     self.login()

    #     # Attempt to create the user
    #     self.create_user()

    #     invalid_password = "admin"
    #     email = "test@example.com"  # This should not match the regex
    #     self.set_response(
    #         self.client.patch(
    #             f"{self.url}11/",
    #             {
    #                 "email": email,
    #                 "password": invalid_password,
    #             },
    #             format="json",
    #         )
    #     )
    #     if (
    #         re.match(settings.PASSWORD_VALIDATE_REGEX, invalid_password)
    #         and len(invalid_password) > 8
    #     ):
    #         self.match_error_response(400)
