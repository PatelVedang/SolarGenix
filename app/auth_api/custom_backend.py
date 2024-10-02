from django.contrib.auth.backends import ModelBackend
from django.utils.timezone import now

from .models import User


class LoginOnAuthBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        """
        This function authenticates a user with the provided email and password, updating the last login
        time if successful.

        :param request: The `request` parameter in the `authenticate` method is typically an HTTP
        request object that contains information about the incoming request, such as headers, cookies,
        and user data. It is commonly used in web frameworks like Django or Flask to handle user
        authentication and authorization
        :param email: The `email` parameter in the `authenticate` method is used to pass the email
        address of the user attempting to authenticate. This email address is typically used along with
        the password to verify the user's identity and grant access to the system
        :param password: The `password` parameter in the `authenticate` method is used to pass the
        user's password for authentication. It is typically used along with the `email` parameter to
        verify the user's credentials during the authentication process. In the provided code snippet,
        the `password` parameter is passed to the `
        :return: The code is returning the user object if authentication is successful, and None if
        there is an exception during the authentication process.
        """
        try:
            # Fetch the user with the given username and check both is_active and is_deleted
            user = User.objects.get(email=email, is_active=True, is_deleted=False)
            # Use Django's built-in check_password method to verify the password
            if user.check_password(password):
                # Update last_login upon successful authentication
                print(user.last_login)
                user.last_login = now()
                user.save()
                print(user.last_login)
                return user
        except User.DoesNotExist:
            return None
