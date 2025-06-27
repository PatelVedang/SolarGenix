import logging

from core.models import Token
from django.utils import timezone

logger = logging.getLogger("django")


def clean_expired_tokens():
    """
    Deletes all expired authentication tokens from the database.

    This function retrieves all tokens whose expiration date is earlier than the current time,
    deletes them, logs the number of deleted tokens, and returns a summary message.

    Returns:
        str: A message indicating the number of expired tokens deleted.
    """
    now = timezone.now()
    expired_tokens = Token.objects.filter(expire_at__lt=now)
    count = expired_tokens.count()
    expired_tokens.delete()
    logger.info(f"Deleting {count} expired tokens...")
    return f"{count} expired tokens deleted."