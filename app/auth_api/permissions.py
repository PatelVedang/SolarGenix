import time

from core.models import Token
from core.services.token_service import TokenService
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import BasePermission

from auth_api.constants import AuthResponseConstants


class IsAuthenticated(BasePermission):
    """
    Custom permission class to check if a user is authenticated and authorized based on the authentication type.

    This permission class supports both Cognito and SimpleJWT authentication mechanisms. It performs the following checks:
    - Ensures the user is authenticated and active.
    - For Cognito authentication:
        - Decodes the provided token and verifies it is an access token.
        - Checks if the token is not expired.
        - Raises an AuthenticationFailed exception if the token is invalid.
    - For SimpleJWT authentication:
        - Decodes the provided token and verifies it is an access token.
        - Checks if the token exists in the database, is not blacklisted, and is not expired.
        - Raises an AuthenticationFailed exception if the token is invalid.

    Returns:
        bool: True if the user passes all authentication and authorization checks, False otherwise.
    """

    def has_permission(self, request, view):
        user = request.user
        auth = request.auth

        # Check if the user is authenticated
        if not user or not user.is_authenticated:
            return False

        # Check if the auth token is provided
        if not user.is_active:
            return False



        try:
            payload = TokenService.decode(str(auth))
        except Exception:
            raise AuthenticationFailed("Invalid token")

        if payload.get("token_type") != "access":
            return False

        tokens = Token.objects.filter(
            jti=payload["jti"],
            user_id=payload["user_id"],
            token_type="access",
            is_blacklist_at__isnull=True,
        )
        if not tokens.exists():
            return False

        token = tokens.first()
        if token.is_expired():
            return False

        return True


class IsManager(BasePermission):
    """
    Custom permission to grant access only to users who are authenticated and belong to the 'Manager' group.

    Methods:
        has_permission(self, request, view): Returns True if the user is authenticated and is a member of the 'Manager' group.
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.groups.filter(name="Manager").exists()
        )


class IsEmployee(BasePermission):
    """
    Custom permission to grant access only to authenticated users who belong to the 'Employee' group.

    Methods:
        has_permission(self, request, view): Returns True if the user is authenticated and is a member of the 'Employee' group.
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.groups.filter(name="Employee").exists()
        )
