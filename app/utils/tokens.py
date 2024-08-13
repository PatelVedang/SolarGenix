# utils/token_utils.py
import jwt
from datetime import datetime
from django.conf import settings
from auth_api.models import Token
from rest_framework_simplejwt.tokens import RefreshToken
from jwt.exceptions import ExpiredSignatureError


def create_token(user, token_type, token=None):
    if token_type not in ["access", "refresh", "reset", "verify", "google"]:
        raise ValueError("Invalid token type")

    if token_type == "google":
        # Assuming google tokens are generated externally and provided as an argument
        token_str = token
        jti = None
        expires_at = None

    else:
        refresh = RefreshToken.for_user(user)
        token = refresh if token_type == "refresh" else refresh.access_token

        if token_type == "reset":
            token = RefreshToken.for_user(user)
            token["token_type"] = "reset"
        elif token_type == "verify":
            token = RefreshToken.for_user(user)
            token["token_type"] = "verify"

        token_str = str(token)
        payload = jwt.decode(token_str, settings.SECRET_KEY, algorithms=["HS256"])
        jti = payload["jti"]
        expires_at = datetime.fromtimestamp(payload["exp"])
    Token.objects.create(
        user=user,
        jti=jti,
        token=token_str,
        token_type=token_type,
        expires_at=expires_at,
    )
    return token_str


def decode_token(token_str):
    return jwt.decode(token_str, settings.SECRET_KEY, algorithms=["HS256"])


def delete_token(token_str):
    try:
        payload = decode_token(token_str)
        Token.objects.filter(jti=payload["jti"]).delete()
    except jwt.ExpiredSignatureError:
        # Handle expired signature if necessary
        raise ExpiredSignatureError("Token is invalid")
    except jwt.InvalidTokenError:
        # Handle invalid token if necessary
        raise jwt.InvalidTokenError("Token Is Invalid")
