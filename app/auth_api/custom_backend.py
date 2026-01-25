import logging

from core.models import User
from core.services.token_service import TokenService
from django.contrib.auth.backends import ModelBackend
from django.utils.timezone import now
from rest_framework.exceptions import AuthenticationFailed

from .constants import AuthResponseConstants

logger = logging.getLogger("django")


class LoginOnAuthBackend(ModelBackend):
    def authenticate(request=None, email=None, password=None, **kwargs):
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
            email = email if email else kwargs.get("email", kwargs.get("username", ""))

            user = User.objects.get(email=email, is_active=True, is_deleted=False)

            if user.check_password(password) and user.is_email_verified:
                # Update the 'last_login' field with the current timestamp upon successful authentication
                user.last_login = now()
                user.save()  # Save the updated 'last_login' field to the database
                try:
                    tokens = TokenService.auth_tokens(user)  # Generation of the Token
                except Exception:
                    # If token generation fails, raise an AuthenticationFailed exception
                    raise AuthenticationFailed(
                        AuthResponseConstants.TOKEN_GENERATION_FAILED
                    )
                # Return the authenticated user object if password validation is successful
                return user, tokens
            else:
                # Return None if the password does not match, indicating failed authentication
                return None
        except User.DoesNotExist:
            raise AuthenticationFailed(AuthResponseConstants.INVALID_CREDENTIALS)



