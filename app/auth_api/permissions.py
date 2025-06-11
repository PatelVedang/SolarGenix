import time

from core.models import SimpleToken, Token
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import BasePermission

from auth_api.cognito import Cognito
from auth_api.constants import AuthResponseConstants


class IsAuthenticated(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        auth = request.auth

        if not user or not user.is_authenticated:
            return False

        if not user.is_active:
            return False

        auth_type = getattr(settings, "AUTH_TYPE", "simplejwt").lower()

        if auth_type == "cognito":
            try:
                payload = Cognito.decode_token(str(auth))
                if payload.get("token_use") != "access":
                    return False
                if payload.get("exp", 0) < time.time():
                    return False
            except Exception:
                raise AuthenticationFailed(AuthResponseConstants.INVALID_COGNITO_TOKEN)
            return True

        try:
            payload = SimpleToken.decode(str(auth))
        except Exception:
            raise AuthenticationFailed(AuthResponseConstants.INVALID_COGNITO_TOKEN)

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
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.groups.filter(name="Manager").exists()
        )


class IsEmployee(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.groups.filter(name="Employee").exists()
        )
