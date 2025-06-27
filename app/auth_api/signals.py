from django.db.models.signals import pre_delete
from django.dispatch import receiver
from core.models import Token, User
from core.services.google_service import Google


@receiver(pre_delete, sender=User)
def revoke_google_access(sender, instance, **kwargs):
    """
    Revokes Google access token for a user instance.

    This signal handler is intended to be called when a user instance is affected (e.g., deleted).
    It checks if the user has an associated Google token, revokes the token using the Google API,
    and then permanently deletes the token from the database.

    Args:
        sender: The model class sending the signal.
        instance: The instance of the user model being processed.
        **kwargs: Additional keyword arguments passed by the signal.

    Side Effects:
        - Calls the Google API to revoke the user's token.
        - Permanently deletes the token from the database if it exists.
    """
    token = Token.objects.filter(user=instance, token_type="google")
    if token.exists():
        token = token.first()
        google = Google()
        google.revoke_token(token.jti)
        token.hard_delete()
