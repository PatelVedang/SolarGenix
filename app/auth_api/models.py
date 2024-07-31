from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from .managers import UserManager,NonDeleted
from django.contrib.auth.models import User
import uuid
from django.core.exceptions import ValidationError

# Create your models here.
class User(AbstractBaseUser):
    email = models.EmailField(
        verbose_name="Email",
        max_length=255,
        unique=True,
    )
    name=models.CharField(max_length=70)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    

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
    class Meta:
            app_label = 'auth_api'
   
    
class Token(models.Model):
    TOKEN_TYPES = (
        ("access", "access"),
        ("refresh", "refresh"),
        ("reset", "reset"),
        ("verify", "verify"),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    jti = models.CharField(max_length=255)
    token=models.CharField(max_length=255)
    token_type = models.CharField(max_length=15, choices=TOKEN_TYPES, default="access")
    expires_at = models.DateTimeField(blank=True, null=True)
    is_blacklisted = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.user.name} - {self.token_type} - {self.jti}"
    
    default = models.Manager()
    objects = NonDeleted()
    
    # def delete(self, *args, **kwargs):
    #     self.is_deleted = True
    #     self.save()
       
    def soft_delete(self):
        self.is_deleted = True
        self.save()

    def restore(self):
        self.is_deleted = False
        self.save()
        
        
class BlacklistToken(models.Model):
    TOKEN_TYPE_CHOICES = [
        ('access', 'Access'),
        ('refresh', 'Refresh'),
        ('reset', 'Reset'),
        ('verify', 'Verify'),
    ]
    token = models.OneToOneField(Token, on_delete=models.CASCADE,null=True)

    jti = models.CharField(max_length=255, unique=True,editable=False)
    token_type = models.CharField(max_length=7, choices=TOKEN_TYPE_CHOICES,editable=False)
    blacklisted_on = models.DateTimeField(auto_now_add=True)
    def save(self, *args, **kwargs):
        if self.token and self.token.is_blacklisted:
            
            self.jti = self.token.jti
            self.token_type = self.token.token_type
            super().save(*args, **kwargs)
        else:
            raise ValidationError("Token is not marked as blacklisted.")
 