# from auth_api.models import BlacklistToken, Token
from core.models import Token
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import BasePermission
from rest_framework_simplejwt.tokens import UntypedToken


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
            Token.objects.get(token=token, is_deleted=False)
        except Token.DoesNotExist:
            raise AuthenticationFailed("Token Does Not Exist")
        validated_token = UntypedToken(token)
        print(validated_token)
        # if BlacklistToken.objects.filter(jti=validated_token.get("jti")).exists():
        #     raise AuthenticationFailed("Token has been blacklisted")

        return True
