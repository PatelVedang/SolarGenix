from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
from user.models import User
import socket

TARGET_STATUS_CHOICES = [
    (0, "Created"),
    (1, "Queued"),
    (2, "Scan in-progress"),
    (3, "Scan terminated"),
    (4, "Scan finished")
]

ORDER_STATUS_CHOICES = [
    (0, "Created"),
    (1, "In Progress"),
    (2, "Failed"),
    (3, "Finished")
]

PAYMENT_STATUS_CHOICES = [
    (0, "Fail"),
    (1, "Success")
]

ACTION_CHOICES = (
        (1, "TARGET_CREATED"),
        (2, "TARGET_IN_QUEUE"),
        (3, "TARGET_TERMINATED"),
        (4, "TARGET_SCANNED"),
        (5, "TARGET_DELETED"),
        (6, "GENERATE_PDF"),
        (7, "GENERATE_HTML")
    )


class NonDeleted(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted = False)
    

class SoftDelete(models.Model):
    is_deleted = models.BooleanField(default=False)

    default = models.Manager()
    objects = NonDeleted()

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.save()

    def soft_delete(self):
        self.is_deleted = True
        self.save()

    def restore(self):
        self.is_deleted = False
        self.save()

    class Meta:
        abstract = True
        ordering = ('-created_at',)
        

# Create your models here.
class Target(SoftDelete):
    ip = models.CharField(max_length=100,null=False)
    raw_result = models.TextField()
    compose_result = models.JSONField(default=dict)
    status = models.IntegerField(choices=TARGET_STATUS_CHOICES, default=0)
    tool = models.ForeignKey("Tool", on_delete=models.SET_NULL, default=1, null=True)
    order = models.ForeignKey("Order", on_delete=models.SET_NULL, null=True, related_name="targets") 
    scan_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    # is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    pdf_path = models.FileField(null=True, blank=True)
    retry= models.BigIntegerField(default=0)
    # scan_time store in seconds
    scan_time = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.ip


class Tool(SoftDelete):
    tool_name = models.CharField(max_length= 50)
    tool_cmd = models.CharField(max_length=500)
    subscription = models.ForeignKey("Subscription", on_delete=models.SET_NULL, null=True, blank=True)
    time_limit = models.BigIntegerField(default=30) 
    # is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    sudo_access = models.BooleanField(default=False)
    py_tool = models.BooleanField(default=False) 

    def __str__(self):
        return self.tool_name
    

class Subscription(SoftDelete):
    day_limit = models.IntegerField()
    price = models.DecimalField(max_digits=11, decimal_places=2)
    plan_type = models.CharField(max_length=255)
    # is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.plan_type


class SubscriptionHistory(models.Model):
    buyer = models.ForeignKey(User, on_delete=models.CASCADE)
    tools_ids = models.TextField(default="1")
    total_price = models.DecimalField(max_digits=11, decimal_places=2)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    status = models.IntegerField(choices=PAYMENT_STATUS_CHOICES, default=0)
    transaction_payload = models.JSONField(default=dict)


class TargetLog(models.Model):
    target = models.ForeignKey(Target, on_delete=models.SET_NULL, null=True)
    action = models.IntegerField(choices=ACTION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True, null=True)


class Order(SoftDelete):
    client = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    subscrib = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True, blank=True)
    target_ip = models.CharField(max_length=100,null=False)
    status = models.IntegerField(choices=ORDER_STATUS_CHOICES, default=0)
    retry= models.BigIntegerField(default=0)
    pdf_path = models.FileField(null=True, blank=True)
    # scan_time store in seconds
    scan_time = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
