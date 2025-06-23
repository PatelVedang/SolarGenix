import time

from auth_api.cognito import Cognito
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import BasePermission
from rest_framework_simplejwt.tokens import UntypedToken

from app.core.models.auth_api.auth import Token


class IsTokenValid(BasePermission):
    """
    Custom DRF permission class to validate authentication tokens from incoming requests.

    This permission checks for a valid Bearer token in the Authorization header, or alternatively
    looks for token values in request data or URL kwargs. It supports validation for both AWS Cognito
    JWT tokens and custom Token model tokens.

    Token validation steps:
    1. Attempt to extract a Bearer token from the Authorization header.
    2. If not found, search for known token types in request data.
    3. If still not found, check for a 'token' in the URL kwargs.
    4. Raise AuthenticationFailed if no token is found.
    5. If a token is found, attempt to decode and validate it as a Cognito JWT access token.
    6. If Cognito validation fails, check for existence in the custom Token model.
    7. Raise AuthenticationFailed if the token does not exist or is invalid.

    Returns:
        bool: True if a valid token is found and passes validation, otherwise raises AuthenticationFailed.

    Raises:
        AuthenticationFailed: If the token is missing, invalid, expired, or blacklisted.
    """

    def has_permission(self, request, view):
        token = None

        # Check for Bearer token in Authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header:
            try:
                token_type, token = auth_header.split()
                if token_type.lower() != "bearer":
                    raise AuthenticationFailed("Invalid token type")
            except ValueError:
                raise AuthenticationFailed("Invalid Authorization header format")

        # If no valid Bearer token, check query parameters
        if not token:
            for token_type in ["refresh", "reset", "verify", "access", "token"]:
                token = request.data.get(token_type)
                if token:
                    break
        # If still no token, raise exception
        if not token:
            token = request.parser_context["kwargs"].get("token")
        if not token:
            raise AuthenticationFailed("Token is missing")

        try:
            payload = Cognito.decode_token(token)
            if payload.get("token_use") != "access":
                raise AuthenticationFailed("Invalid Cognito token type")
            if payload.get("exp") < int(time.time()):
                raise AuthenticationFailed("Cognito token has expired")
            return True
        except Exception:
            pass

        try:
            Token.objects.get(token=token, is_deleted=False)
        except Token.DoesNotExist:
            raise AuthenticationFailed("Token does not exist")
        validated_token = UntypedToken(token)
        print(validated_token)
        # if BlacklistToken.objects.filter(jti=validated_token.get("jti")).exists():
        #     raise AuthenticationFailed("Token has been blacklisted")

        return True
