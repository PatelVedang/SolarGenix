import string
import uuid
from django.db import models
from django.utils.crypto import get_random_string


class NonDeleted(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
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

    def hard_delete(self):
        super().delete()

    class Meta:
        abstract = True
        ordering = ("-created_at",)


def generate_password():
    """Generates a random password with letters, digits, and punctuation."""
    allowed_chars = string.ascii_letters + string.digits + string.punctuation
    return get_random_string(8, allowed_chars)


