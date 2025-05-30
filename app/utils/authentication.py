from django.utils.translation import gettext as _
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from user_auth.constants import AuthResponseConstants


class CustomJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        user = super().get_user(validated_token)

        # Check if the user is marked as deleted
        if user.is_deleted:
            raise AuthenticationFailed(
                _(AuthResponseConstants.ACCOUNT_DELETED), code="user_deleted"
            )

        return user
