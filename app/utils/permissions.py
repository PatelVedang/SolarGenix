import time
from rest_framework.permissions import BasePermission
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import BasePermission
from rest_framework_simplejwt.tokens import UntypedToken
from app.core.models.auth_api.auth import Token
from auth_api.cognito import Cognito


class IsTokenValid(BasePermission):
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
            payload = Cognito.decode(token)
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
