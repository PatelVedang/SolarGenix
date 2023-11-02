from django.db import models
from user.models import User

# Create your models here.
class PaymentHistory(models.Model):
    STATUS_CHOICES = (
        (1, 'Active'),
        (2, 'Canceled'),
        (3, 'Paused'),
    )
    PRICE_TYPE_CHOICE = (
        (1, 'Recurring Monthly'),
        (2, 'Recurring Annualy'),
        (3, 'One Time')
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    stripe_subscription_id = models.CharField(max_length=255, null=True)
    price_id = models.CharField(max_length=255)
    status = models.IntegerField(choices=STATUS_CHOICES, default=1)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    current_period_start = models.DateTimeField()
    current_period_end = models.DateTimeField(null=True)
    ip_limit = models.IntegerField(default=1)
    price_type = models.IntegerField(choices=PRICE_TYPE_CHOICE, default=1)
    
