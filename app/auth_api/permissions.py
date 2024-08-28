from rest_framework.permissions import BasePermission
from .models import Token, SimpleToken


class IsAuthenticated(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if not request.user.is_active:
            return False

        payload = SimpleToken.decode(str(request.auth))
        if payload.get("token_type") != "access":
            return False

        token = Token.objects.filter(
            jti=payload["jti"],
            user_id=payload["user_id"],
            token_type="access",
            is_blacklist_at__isnull=True,
        )

        if not token.exists():
            return False

        return True
