from django.db import models
from datetime import datetime
from django.contrib.auth.models import User

TOOL_CHOICES = [
    ("nmap", "nmap")
]

# Create your models here.
class Machine(models.Model):
    ip = models.CharField(max_length=15,null=False)
    client = models.CharField(max_length=15)
    result = models.TextField()
    scanned = models.BooleanField(default=False)
    bg_task_status =  models.BooleanField(default=False)
    tool = models.CharField(choices=TOOL_CHOICES, default='nmap', max_length=50)
    created_at = models.DateTimeField(null=False, default=datetime.now())
    updated_at = models.DateTimeField(null=False,default=datetime.now())

    def __str__(self):
        return self.ip 
    
 