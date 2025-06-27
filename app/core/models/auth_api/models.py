import logging
import uuid

from auth_api.managers import UserManager
from django.contrib.auth.models import AbstractUser, Group, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from proj.models import BaseModel

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
