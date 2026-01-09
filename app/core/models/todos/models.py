from django.db import models
import uuid
from proj.models import BaseModel

class Todo(BaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    inventory = models.IntegerField()
    available = models.BooleanField(default=True)
    published_date = models.DateField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    rating = models.FloatField(default=1)
    image = models.ImageField(upload_to='images/',null=True,blank=True)
    file = models.FileField(upload_to='files/',null=True,blank=True)
    url = models.URLField(default='http://test.com')
    email = models.EmailField(default='test@yopmail.com')
    slug = models.SlugField(default='test-slug')
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    ip_address = models.GenericIPAddressField(default='127.0.0.1')
    big_integer = models.BigIntegerField(default='0')
    positive_integer = models.PositiveIntegerField(default='1')
    small_integer = models.SmallIntegerField(default='0')
    duration = models.DurationField(default='00:00:00')
    json_data = models.JSONField(default=dict)

    def __str__(self):
        return self.name
