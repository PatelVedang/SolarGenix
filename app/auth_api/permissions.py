import time
from rest_framework.permissions import BasePermission

from core.models import Token, SimpleToken
from core.services.token_service import TokenService
from auth_api.cognito import Cognito
from rest_framework.exceptions import AuthenticationFailed


class IsAuthenticated(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        auth = request.auth

        if not user or not user.is_authenticated:
            return False

        if not user.is_active:
            return False
        payload = TokenService.decode(str(request.auth))

        if getattr(user, "auth_provider", None) == "cognito":
            try:
                payload = Cognito.decode_token(str(auth))
                if payload.get("token_use") != "access":
                    return False
                if payload.get("exp", 0) < time.time():
                    return False
            except Exception:
                raise AuthenticationFailed("Invalid Cognito token")
            return True

        try:
            payload = SimpleToken.decode(str(auth))
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
