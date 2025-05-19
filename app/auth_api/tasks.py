from celery import shared_task
from auth_api.models import Token  # replace with your actual token model
from django.utils import timezone

@shared_task
def clean_expired_tokens():
    now = timezone.now()
    expired_tokens = Token.objects.filter(expire_at__lt=now)
    count = expired_tokens.count()
    expired_tokens.delete()
    return f"{count} expired tokens deleted."