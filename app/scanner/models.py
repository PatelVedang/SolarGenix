from django.db import models
from datetime import datetime
from django.contrib.auth.models import User

STATUS_CHOICES = [
    (0, "Created"),
    (1, "Queued"),
    (2, "Scan started"),
    (3, "Scan terminated "),
    (4, "Scan finished")
]

# Create your models here.
class Machine(models.Model):
    ip = models.CharField(max_length=15,null=False)
    client = models.CharField(max_length=15)
    result = models.TextField()
    # scanned = models.BooleanField(default=False)
    # bg_task_status =  models.BooleanField(default=False)
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    tool = models.ForeignKey("Tool", on_delete=models.CASCADE , null=True)
    created_at = models.DateTimeField(null=False, default=datetime.now())
    updated_at = models.DateTimeField(null=False,default=datetime.now())

    def __str__(self):
        return self.ip

class Tool(models.Model):
    tool_name = models.CharField(max_length= 50)
    tool_cmd = models.CharField(max_length=500)
    created_at = models.DateTimeField(null=False, default=datetime.now())
    updated_at = models.DateTimeField(null=False,default=datetime.now())

    def __str__(self):
        return self.tool_name
    