from django.urls import reverse
from auth_api.tests import BaseAPITestCase


class UserTestCase(BaseAPITestCase):
    url = reverse("user-list")
    super_admin_email = "superadmin@gmail.com"
    super_admin_password = "Admin@1234"

    def temp_payload(self, **kwargs):
        if not kwargs:
            data = {
                "first_name": "New",
                "last_name": "User",
                "email": "new@example.com",
                "password": "Admin@1234",
                "auth_provider": "email",
                "is_active": True,
                "is_superuser": False,
                "is_staff": False,
            }
        else:
            data = kwargs
        return {**data}

    def create_user(self, **kwargs):
        self._data = self.temp_payload(**kwargs)
        print(self._data, "create_user>>>>>>>>>>>>>>>>>>>")
        self.set_response(self.client.post(self.url, self._data, format="multipart"))

    # def test_create_users_with_authenticate(self):
    #     """
    #     The function `test_create_users_with_authenticate` creates a user with authentication
    #     and checks for a successful response.
    #     """
    #     self.login()
    #     self.create_user()
    #     self.match_success_response(201)

    # def test_create_users_without_authenticate(self):
    #     """
    #     The function `test_create_users_without_authenticate` creates a user without authentication
    #     and checks for a successful response.
    #     """
    #     self.create_user()
    #     self.match_error_response(401)

    # def test_user_email_invalid(self):
    #     """
    #     The function `test_user_email_invalid` creates a user with an invalid email address and
    #     checks for a validation error.
    #     """
    #     self.login()
    #     self.create_user(email="test")
    #     self.match_error_response(400)

    # def test_user_email_exists(self):
    #     """
    #     The function `test_user_email_exists` creates a user with an email address that already exists and
    #     checks for a validation error.
    #     """
    #     self.login()
    #     self.create_user(email="test@example.com")
    #     self.create_user(email="test@example.com")
    #     self.match_error_response(400)

    # def test_user_password_invalid(self):
    #     """
    #     The function `test_user_password_invalid` creates a user with an invalid password and
    #     checks for a validation error.
    #     """
    #     self.login()
    #     invalid_password = "admin"  # This should not match the regex
    #     kwargs = self.temp_payload(email="test@example.com", password=invalid_password)

    #     # Attempt to create the user
    #     self.create_user(**kwargs)

    #     # Manually check if the password is invalid and then call the appropriate response matcher
    #     if re.match(settings.PASSWORD_VALIDATE_REGEX, invalid_password) and len(invalid_password) > 8:
    #         self.match_error_response(400)

    # def test_get_user_default_query(self):
    #     """
    #     The function `test_get_user_default_query` retrieves users with default query parameters
    #     and checks for a successful response.
    #     """
    #     self.login()
    #     response = self.client.get(self.url)
    #     self.assertEqual(response.status_code, 200)

    # def test_get_users_without_authenticate(self):
    #     """
    #     The function `test_get_users_without_authenticate` retrieves users without authentication
    #     and checks for a successful response.
    #     """
    #     response = self.client.get(self.url)
    #     self.assertEqual(response.status_code, 401)

    # def test_get_user_first_name_filter(self):
    #     """
    #     The function `test_get_user_first_name_filter` retrieves users by first name filter
    #     and checks for a successful response.
    #     """
    #     self.login()
    #     self.client.get(f"{self.url}?first_name=yash")
    #     self.match_success_response(200)

    def test_get_user_by_admin(self):
        """
        The function `test_get_user_by_id` retrieves a user by ID and checks for a successful response.
        """
        self.login()
        self.create_user()
        self.set_response(self.client.get(f"{self.url}2/"))
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
