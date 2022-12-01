from django.db import models
from datetime import datetime

# Create your models here.
class Machine(models.Model):
    ip = models.CharField(max_length=15,null=False)
    result = models.TextField()
    scanned = models.BooleanField(default=False)
    created_at = models.DateTimeField(null=False, default=datetime.now())
    updated_at = models.DateTimeField(null=False,default=datetime.now())

    def __str__(self):
        return self.ip 
    
 