from django.db import models
import uuid
from proj.models import BaseModel


class Todo(BaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    inventory = models.IntegerField()
    available = models.BooleanField(default=True)
    published_date = models.DateField()
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    rating = models.FloatField()
    image = models.ImageField(upload_to="images/")
    file = models.FileField(upload_to="files/")
    url = models.URLField()
    email = models.EmailField()
    slug = models.SlugField()
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    ip_address = models.GenericIPAddressField()
    big_integer = models.BigIntegerField()
    positive_integer = models.PositiveIntegerField()
    small_integer = models.SmallIntegerField()
    duration = models.DurationField()
    json_data = models.JSONField()

    def __str__(self):
        return self.name
