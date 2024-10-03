import logging
import uuid
from datetime import datetime, timedelta

import jwt
from django.conf import settings
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from proj.models import BaseModel
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.tokens import Token as BaseToken
from utils.custom_exception import CustomValidationError as ValidationError

from .managers import UserManager

logger = logging.getLogger("django")


class TokenType(models.TextChoices):
    ACCESS = "access", ("Access")
    REFRESH = "refresh", ("Refresh")
    RESET = "reset", ("Reset")
    VERIFY_MAIL = "verify_mail", ("Verify Mail")
    GOOGLE = "google", ("Google")
    OTP = "otp", ("Otp")


class SimpleToken(BaseToken):
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
            raise ValidationError("Invalid token")
        jti = payload["jti"]
        user_id = payload["user_id"]
        token = Token.objects.filter(
            jti=jti,
            user_id=user_id,
            token_type=token_type,
            is_blacklist_at__isnull=True,
        )
        if token.exists():
            token = token.first()
            if token.is_expired():
                token.hard_delete()
                raise AuthenticationFailed("Token has expired")
            payload["token_obj"] = token
            return payload
        else:
            raise AuthenticationFailed("Invalid token")


# Create your models here.
AUTH_PROVIDER = {"google": "google", "email": "email"}


class User(AbstractUser, PermissionsMixin, BaseModel):
    username = None
    email = models.EmailField(
        verbose_name="Email",
        max_length=255,
        unique=True,
    )
    auth_provider = models.CharField(
        max_length=255, null=False, blank=False, default=AUTH_PROVIDER.get("email")
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,  # Override the default value
    )
    is_email_verified = models.BooleanField(default=False)
    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        self.email = self.email.lower()  # Normalize email to lowercase
        super().save(*args, **kwargs)

    def auth_tokens(self):
        refresh_token = RefreshToken.for_user(self)
        access_token = refresh_token.access_token
        jti = access_token["jti"]
        refresh_token["jti"] = jti
        Token.objects.bulk_create(
            [
                Token(
                    user=self,
                    jti=access_token["jti"],
                    token_type=access_token.token_type,
                    expire_at=datetime.fromtimestamp(access_token["exp"]),
                ),
                Token(
                    user=self,
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

    class Meta:
        app_label = "auth_api"


class Token(BaseModel):  # Inherits from BaseClass
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    jti = models.CharField(max_length=255, default=uuid.uuid4().hex)
    token = models.TextField(null=True, blank=True)
    token_type = models.CharField(max_length=15, choices=TokenType, default="access")
    expire_at = models.DateTimeField(blank=True, null=True)
    is_blacklist_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.user} - {self.token_type}"

    def is_expired(self):
        if self.expire_at:
            return timezone.now() >= self.expire_at
        return False

    def blacklist(self):
        self.is_blacklist_at = timezone.now()
        self.save()
