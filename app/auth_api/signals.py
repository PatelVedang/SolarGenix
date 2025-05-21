from django.db.models.signals import pre_delete
from django.dispatch import receiver
from core.models import Token, User
from .google import Google


@receiver(pre_delete, sender=User)
def revoke_google_access(sender, instance, **kwargs):
    token = Token.objects.filter(user=instance, token_type="google")
    if token.exists():
        token = token.first()
        google = Google()
        google.revoke_token(token.jti)
        token.hard_delete()
