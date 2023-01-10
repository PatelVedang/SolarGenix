from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
from user.models import User

STATUS_CHOICES = [
    (0, "Created"),
    (1, "Queued"),
    (2, "Scan started"),
    (3, "Scan terminated"),
    (4, "Scan finished")
]

# Create your models here.
class Machine(models.Model):
    ip = models.CharField(max_length=15,null=False)
    result = models.TextField()
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    tool = models.ForeignKey("Tool", on_delete=models.CASCADE, default=1)
    scan_by = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.ip

class Tool(models.Model):
    tool_name = models.CharField(max_length= 50)
    tool_cmd = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.tool_name