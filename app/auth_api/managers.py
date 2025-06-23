from django.contrib.auth.models import BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        Creates and saves a User with the given email and password.

        Args:
            email (str): The user's email address. Must be provided.
            password (str, optional): The user's password. Defaults to None.
            **extra_fields: Additional fields to set on the user object.

        Raises:
            ValueError: If the email is not provided.

        Returns:
            User: The newly created user instance.
        """
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(email=self.normalize_email(email), **extra_fields)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Creates and returns a superuser with the given email and password.

        This method sets default values for required superuser fields such as
        'is_staff', 'is_superuser', 'is_active', and 'is_email_verified'. It also
        assigns default values for 'first_name' and 'last_name' if they are not
        provided in extra_fields. Raises a ValueError if 'is_staff' or
        'is_superuser' are not set to True.

        Args:
            email (str): The email address of the superuser.
            password (str, optional): The password for the superuser.
            **extra_fields: Additional fields to set on the superuser.

        Returns:
            User: The created superuser instance.

        Raises:
            ValueError: If 'is_staff' or 'is_superuser' are not set to True.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_email_verified", True)
        extra_fields.setdefault("first_name", extra_fields.get("first_name", "admin"))
        extra_fields.setdefault("last_name", extra_fields.get("last_name", "admin"))

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(email, password, **extra_fields)

    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False, is_active=True)


class NonDeleted(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)
