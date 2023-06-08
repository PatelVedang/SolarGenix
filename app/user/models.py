from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from .managers import UserManager
from django.utils.translation import gettext_lazy as _
from datetime import datetime

# Create your models here.
class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        (1, "Super admin"),
        (2, "User"),
    )
    username = None
    email = models.EmailField(_('email address'), unique=True, blank=False, null=False)
    # is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    first_name = models.CharField(max_length=50) 
    last_name = models.CharField(max_length=50)
    role = models.IntegerField(default=2)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, null=True)
    otp_expires = models.DateTimeField(auto_now_add=True, null=True)
    subscription = models.ForeignKey('scanner.Subscription', on_delete=models.SET_NULL, null=True, blank=True, default=1)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        self.first_name = self.first_name.lower()
        self.last_name = self.last_name.lower()
        self.email = self.email.lower()
        return super(User, self).save(*args, **kwargs)
    