from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from .managers import UserManager
from django.utils.translation import gettext_lazy as _
from datetime import datetime
from django.db.models import Q
from datetime import datetime
from payments.models import PaymentHistory

# Create your models here.
class Role(models.Model):
    name = models.CharField(max_length=50)
    tool_access = models.BooleanField(default=False)
    target_access = models.BooleanField(default=False)
    client_name_access = models.BooleanField(default=True)
    scan_result_access = models.BooleanField(default=False)
    cover_content_access = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name
    class Meta:
        ordering = ('-created_at',)

class User(AbstractBaseUser, PermissionsMixin):
    LANGUAGE_CHOICE = (
        ('EN', 'EN'),
        ('FR', 'FR')
    )


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
    stripe_customer_id = models.CharField(max_length=255, null=True)
    report_language = models.CharField(max_length=10, choices=LANGUAGE_CHOICE,default='EN')

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
    
    def get_active_plan(self):
        today = datetime.utcnow()
        return PaymentHistory.objects.filter(
            Q(status=1) &
            Q(user=self) &
            Q(current_period_start__lte=today) &
            (Q(current_period_end__isnull=True) |
            Q(current_period_end__gte=today))
        ).order_by('-created_at')
    
    class Meta:
        ordering = ('-created_at',)
    