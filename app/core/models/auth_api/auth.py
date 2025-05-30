import logging
import uuid
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from proj.models import BaseModel
from auth_api.managers import UserManager

logger = logging.getLogger("django")

class TokenType(models.TextChoices):
    ACCESS = "access", ("Access")
    REFRESH = "refresh", ("Refresh")
    RESET = "reset", ("Reset")
    VERIFY_MAIL = "verify_mail", ("Verify Mail")
    GOOGLE = "google", ("Google")
    OTP = "otp", ("Otp")

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
    is_default_password = models.BooleanField(default=False)
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
    jti = models.CharField(max_length=255)
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
