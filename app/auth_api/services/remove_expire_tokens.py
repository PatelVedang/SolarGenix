import logging

from core.models import Token
from django.utils import timezone

logger = logging.getLogger("django")


def clean_expired_tokens():
    now = timezone.now()
    expired_tokens = Token.objects.filter(expire_at__lt=now)
    count = expired_tokens.count()
    expired_tokens.delete()
    logger.info(f"Deleting {count} expired tokens...")
    return f"{count} expired tokens deleted."