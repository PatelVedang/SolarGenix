from auth_api.constants import AuthResponseConstants
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed

User = get_user_model()


class CustomJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication class that extends the base JWTAuthentication.
    Overrides:
        get_user(validated_token):
            Retrieves the user associated with the validated JWT token.
            Raises an AuthenticationFailed exception if the user is marked as deleted.
    Raises:
        AuthenticationFailed: If the user is marked as deleted.
    Returns:
        User instance if authentication is successful and the user is not deleted.
    """
 
    def get_user(self, validated_token):
        user = super().get_user(validated_token)

        # Check if the user is marked as deleted
        if user.is_deleted:
            raise AuthenticationFailed(
                _(AuthResponseConstants.ACCOUNT_DELETED), code="user_deleted"
            )

        return user



