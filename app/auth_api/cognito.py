import logging
import jwt
import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.exceptions import AuthenticationFailed
from .models import Token

User = get_user_model()

logger = logging.getLogger(__name__)


class Cognito:
    @staticmethod
    def decode_token(token: str):
        """
        Decode and return payload from a Cognito JWT token (signature not verified).
        """
        try:
            return jwt.decode(
                token, options={"verify_signature": False}, algorithms=["RS256"]
            )
        except Exception as e:
            raise AuthenticationFailed(f"Invalid token: {str(e)}")

    @staticmethod
    def exchange_code_for_tokens(code: str) -> dict:
        data = {
            "grant_type": "authorization_code",
            "client_id": settings.COGNITO_CLIENT_ID,
            "client_secret": settings.COGNITO_CLIENT_SECRET,
            "code": code,
            "redirect_uri": settings.COGNITO_REDIRECT_URI,
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }
        cognito_token_url = f"{settings.COGNITO_DOMAIN}/oauth2/token"
        response = requests.post(cognito_token_url, data=data, headers=headers)
        if response.status_code != 200:
            raise Exception("Token exchange failed")
        return response.json()

    @classmethod
    def logout_user(cls, user):
        """
        Simulates logout by removing locally stored Cognito tokens
        (access_token, refresh_token, id_token).
        """
        deleted, _ = Token.objects.filter(
            user=user,
            token_type__in=["access_token", "refresh_token", "id_token"],
            is_blacklist_at__isnull=True,
        ).delete()

        logger.info(f"[Cognito Logout] Removed {deleted} token(s) for user {user.id}")
