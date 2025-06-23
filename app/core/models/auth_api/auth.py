import logging
import uuid
from datetime import datetime, timedelta

import jwt
from auth_api.managers import UserManager
from django.conf import settings
from django.contrib.auth.models import AbstractUser, Group, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from proj.models import BaseModel
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import Token as BaseToken

logger = logging.getLogger("django")


# TokenType Enum for different token types (similar to Django's TextChoices)
class TokenType(models.TextChoices):
    ACCESS = "access", ("Access")
    REFRESH = "refresh", ("Refresh")
    RESET = "reset", ("Reset")
    VERIFY_MAIL = "verify_mail", ("Verify Mail")
    GOOGLE = "google", ("Google")
    OTP = "otp", ("Otp")
    ID_TOKEN = "id_token", ("Id Token")


class SimpleToken(BaseToken):
    """A simple token class that extends the BaseToken from SimpleJWT.
    This class is used to create and validate tokens for user authentication.
    It includes methods for creating tokens, decoding them, and validating"""

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
        Creates and returns a token instance for the specified user and token type.

        This method generates a token with the given type and lifetime, associates it with the user,
        and stores relevant information such as the token's unique identifier (jti) and user ID.
        If the token type is not 'access' or 'refresh', any existing tokens of the same type for the user are deleted.
        A new Token object is then created and saved to the database with the appropriate expiration time.

        Args:
            user (User): The user instance for whom the token is being created.
            token_type (str): The type of token to create (e.g., 'access', 'refresh', or custom types).
            lifetime (timedelta): The duration for which the token is valid.
            jti (str, optional): A unique identifier for the token. If not provided, a new one is generated.

        Returns:
            Token: The generated token instance.
        """
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
        """
        Decodes a JWT token using the application's secret key.

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
        Validates a JWT token by decoding its payload, verifying its type, and checking its existence and validity in the database.

        Args:
            token (str): The JWT token string to be validated.
            token_type (str): The expected type of the token (e.g., 'access', 'refresh').

        Returns:
            dict: The decoded payload of the token with an additional 'token_obj' key containing the Token instance.

        Raises:
            AuthenticationFailed: If the token type is invalid, the token does not exist, is blacklisted, expired, or the associated user is inactive or deleted.
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


# Create your models here.
AUTH_PROVIDER = {"google": "google", "email": "email", "cognito": "cognito"}


class User(AbstractUser, PermissionsMixin, BaseModel):
    """Custom User model that extends AbstractUser and PermissionsMixin."""

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
    is_default_password = models.BooleanField(default=False)
    cognito_sub = models.CharField(max_length=255, unique=True, null=True, blank=True)
    totp_secret = models.CharField(max_length=64, null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        self.email = self.email.lower()  # Normalize email to lowercase
        super().save(*args, **kwargs)

    class Meta:
        app_label = "core"


class Token(BaseModel):  # Inherits from BaseClass
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    jti = models.CharField(max_length=255, null=True, blank=True)
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


class GroupProfile(models.Model):
    """
    Represents a profile associated with a Django auth Group, allowing additional metadata
    such as a redirect URL for users belonging to the group.

    Attributes:
        group (Group): The Django auth Group this profile is associated with (one-to-one).
        redirect_url (str): URL to redirect users of this group. Defaults to "/".

    Methods:
        __str__(): Returns a string representation of the group profile.
    """

    group = models.OneToOneField(
        Group, on_delete=models.CASCADE, related_name="profile"
    )
    redirect_url = models.URLField(
        help_text="URL to redirect users of this group", default="/"
    )

    def __str__(self):
        return f"{self.group.name} Profile"
