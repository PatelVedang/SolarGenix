from django.db import models
from .managers import UserManager, NonDeleted
import uuid
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


# Create your models here.
AUTH_PROVIDER = {"google": "google", "email": "email"}


class User(AbstractUser, PermissionsMixin):
    username = None
    email = models.EmailField(
        verbose_name="Email",
        max_length=255,
        unique=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    auth_provider = models.CharField(
        max_length=255, null=False, blank=False, default=AUTH_PROVIDER.get("email")
    )
    is_active = models.BooleanField(
        _("active"),
        default=False,  # Override the default value
    )
    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.first_name

    def save(self, *args, **kwargs):
        self.email = self.email.lower()  # Normalize email to lowercase
        super().save(*args, **kwargs)

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return self.is_superuser

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    # @property
    # def is_staff(self):
    #     "Is the user a member of staff?"
    #     # Simplest possible answer: All admins are staff
    #     return self.is_staff

    class Meta:
        app_label = "auth_api"


class Token(models.Model):
    TOKEN_TYPES = (
        ("access", "access"),
        ("refresh", "refresh"),
        ("reset", "reset"),
        ("verify", "verify"),
        ("google", "google"),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    jti = models.CharField(max_length=255, null=True, blank=True)
    token = models.CharField(max_length=255)
    token_type = models.CharField(max_length=15, choices=TOKEN_TYPES, default="access")
    expires_at = models.DateTimeField(blank=True, null=True)
    is_blacklisted = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.first_name} - {self.token_type} - {self.jti}"

    default = models.Manager()
    objects = NonDeleted()

    def soft_delete(self):
        self.is_deleted = True
        self.save()

    def restore(self):
        self.is_deleted = False
        self.save()


class BlacklistToken(models.Model):
    TOKEN_TYPE_CHOICES = [
        ("access", "Access"),
        ("refresh", "Refresh"),
        ("reset", "Reset"),
        ("verify", "Verify"),
    ]
    token = models.OneToOneField(Token, on_delete=models.CASCADE, null=True)

    jti = models.CharField(max_length=255, unique=True, editable=False)
    token_type = models.CharField(
        max_length=7, choices=TOKEN_TYPE_CHOICES, editable=False
    )
    blacklisted_on = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.token and self.token.is_blacklisted:
            self.jti = self.token.jti
            self.token_type = self.token.token_type
            super().save(*args, **kwargs)
        else:
            raise ValidationError("Token is not marked as blacklisted.")
