from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from .managers import UserManager
from django.utils.translation import gettext_lazy as _
from datetime import datetime

# Create your models here.
class Role(models.Model):
    name = models.CharField(max_length=50)
    tool_access = models.BooleanField(default=False)
    target_access = models.BooleanField(default=False)
    client_name_access = models.BooleanField(default=True)
    scan_result_access = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name
    class Meta:
        ordering = ('-created_at',)

class User(AbstractBaseUser, PermissionsMixin):
    def upload_profile_to(instance, filename):
        return f'profiles/{instance.id}/{filename}'
    username = None
    email = models.EmailField(_('email address'), unique=True, blank=False, null=False)
    # is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    role = models.ForeignKey("Role", on_delete=models.SET_NULL, null=True, blank=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, null=True)
    otp_expires = models.DateTimeField(auto_now_add=True, null=True)
    subscription = models.ForeignKey('scanner.Subscription', on_delete=models.SET_NULL, null=True, blank=True, default=1)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    is_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=255, null=True, blank=True)
    token_expiration = models.DateTimeField(null=True, blank=True)
    mobile_number = models.CharField(max_length=13, null=True, blank=True) 
    country_code = models.CharField(max_length=13, null=True, blank=True) 
    profile_image = models.ImageField(upload_to=upload_profile_to, null=True, blank=True)
    user_company = models.CharField(max_length=1000, blank=True)
    user_address = models.TextField(blank=True)

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
    
    class Meta:
        ordering = ('-created_at',)
    