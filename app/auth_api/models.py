import uuid

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.exceptions import ValidationError
from django.db import models


# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self, email, name, tc, password=None, password2=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=self.normalize_email(email),
            name=name,
            tc=tc,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, tc, password=None):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password,
            name=name,
            tc=tc,
        )
        user.is_active = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


AUTH_PROVIDER = {"google": "google", "email": "email"}


class User(AbstractBaseUser):
    email = models.EmailField(
        verbose_name="Email",
        max_length=255,
        unique=True,
    )
    name = models.CharField(max_length=70)
    tc = models.BooleanField()
    is_active = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    auth_provider = models.CharField(
        max_length=255, null=False, blank=False, default=AUTH_PROVIDER.get("email")
    )
    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "tc"]

    def __str__(self):
        return self.name

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return self.is_superuser

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_superuser

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
    jti = models.CharField(max_length=255)
    token = models.CharField(max_length=255)
    token_type = models.CharField(max_length=15, choices=TOKEN_TYPES, default="access")
    expires_at = models.DateTimeField(blank=True, null=True)
    is_blacklisted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.name} - {self.token_type} - {self.jti}"


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
