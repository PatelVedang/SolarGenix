import logging
from datetime import datetime, timedelta

import jwt
from core.models import Token
from django.conf import settings
from django.utils import timezone
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.tokens import Token as BaseToken

logger = logging.getLogger("django")


class TokenService(BaseToken):
    def __init__(self, token_type=None, lifetime=None, *args, **kwargs):
        self.token_type = token_type
        self.lifetime = (
            timedelta(days=365 * 100)
            if lifetime is None
            else timedelta(minutes=lifetime)
        )
        super().__init__(*args, **kwargs)

    @classmethod
    def for_user(cls, user, token_type, lifetime, jti=None):
        """
        Generates and stores a token for a given user.

        Args:
            user (User): The user instance for whom the token is being generated.
            token_type (str): The type of token to generate (e.g., "access", "refresh", or custom types).
            lifetime (timedelta): The duration for which the token is valid.
            jti (str, optional): The JWT ID for the token. If not provided, a new one is generated.

        Returns:
            Token: The generated token instance.

        Side Effects:
            - Deletes existing tokens of the same custom type for the user (if token_type is not "access" or "refresh").
            - Creates and stores a new token in the database.
        """
        token = cls(token_type=token_type, lifetime=lifetime)
        token["jti"] = jti or token["jti"]
        token["user_id"] = str(user.id)
        if token_type not in ["access", "refresh"]:
            Token.default.filter(user=user, token_type=token_type).delete()
        Token.objects.create(
            user=user,
            jti=token["jti"],
            token_type=token.token_type,
            expire_at=timezone.make_aware(
                datetime.fromtimestamp(token["exp"])
            ),  # Ensure timezone-aware datetime
        )
        return token

    @classmethod
    def decode(cls, token):
        """
        Decodes a JWT token using the application's secret key.

        Attempts to decode the provided JWT token with the HS256 algorithm.
        Raises an AuthenticationFailed exception if the token is expired, invalid, or cannot be decoded.

        Args:
            token (str): The JWT token to decode.

        Returns:
            dict: The decoded payload of the JWT token.

        Raises:
            AuthenticationFailed: If the token is expired, invalid, or cannot be decoded.
        """
        try:
            return jwt.decode(
                token, settings.SECRET_KEY, algorithms=["HS256"], verify=True
            )
        except jwt.ExpiredSignatureError as e:
            logger.error("Token has expired with error: %s", e)
            raise AuthenticationFailed("Token has expired")
        except jwt.DecodeError as e:
            logger.error("Invalid token with error: %s", e)
            raise AuthenticationFailed("Invalid token")
        except jwt.InvalidTokenError as e:
            logger.error("Invalid token with error: %s", e)
            raise AuthenticationFailed("Invalid token")

    @classmethod
    def validate_token(cls, token, token_type):
        """
        Validates a given token by decoding its payload, checking its type, and ensuring it exists and is valid in the database.

        Args:
            token (str): The JWT token string to be validated.
            token_type (str): The expected type of the token (e.g., 'access', 'refresh').

        Returns:
            dict: The decoded payload of the token with an additional "token_obj" key containing the Token instance.

        Raises:
            AuthenticationFailed: If the token is invalid, expired, blacklisted, or associated with an inactive or deleted user.
        """
        payload = cls.decode(token)

        if payload["token_type"] != token_type:
            raise AuthenticationFailed("Invalid token")
        jti = payload["jti"]
        user_id = payload["user_id"]
        # user_obj = User.objects.filter(id=user_id).first()

        token = Token.objects.filter(
            jti=jti,
            user_id=user_id,
            token_type=token_type,
            is_blacklist_at__isnull=True,
        ).first()
        if token:
            if token.is_expired():
                token.hard_delete()
                raise AuthenticationFailed("Token has expired")
            if not token.user.is_active or token.user.is_deleted:
                raise AuthenticationFailed("Invalid token")
            payload["token_obj"] = token
            return payload
        else:
            raise AuthenticationFailed("Invalid token")

    @classmethod
    def auth_tokens(cls, user):
        """
        Generates and stores authentication tokens (access and refresh) for a given user.

        This method creates JWT access and refresh tokens for the specified user, saves their metadata
        (including user, token type, unique identifier (jti), and expiration time) in the Token model,
        and returns the tokens along with their expiration timestamps.

        Args:
            user (User): The user instance for whom the tokens are being generated.

        Returns:
            dict: A dictionary containing the access and refresh tokens and their expiration times.
                Example:
                    {
                        "access": {"token": "<access_token>", "expires": <access_expiry_timestamp>},
                        "refresh": {"token": "<refresh_token>", "expires": <refresh_expiry_timestamp>},
        """
        refresh_token = RefreshToken.for_user(user)
        access_token = refresh_token.access_token
        jti = access_token["jti"]
        refresh_token["jti"] = jti

        Token.objects.bulk_create(
            [
                Token(
                    user=user,
                    jti=access_token["jti"],
                    token_type=access_token.token_type,
                    expire_at=datetime.fromtimestamp(access_token["exp"]),
                ),
                Token(
                    user=user,
                    jti=refresh_token["jti"],
                    token_type=refresh_token.token_type,
                    expire_at=datetime.fromtimestamp(refresh_token["exp"]),
                ),
            ]
        )

        return {
            "access": {"token": str(access_token), "expires": access_token["exp"]},
            "refresh": {
                "token": str(refresh_token),
                "expires": refresh_token["exp"],
            },
        }
