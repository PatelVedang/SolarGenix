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
        token = cls(token_type=token_type, lifetime=lifetime)
        token["jti"] = jti or token["jti"]
        token["user_id"] = user.id
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
    def auth_tokens(cls ,user):
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