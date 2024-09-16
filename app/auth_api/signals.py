from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver
from .models import Token, User
from .google import Google


@receiver(pre_delete, sender=User)
def revoke_google_access(sender, instance, **kwargs):
    token = Token.objects.filter(user=instance, token_type="google")
    if token.exists():
        token = token.first()
        google = Google()
        google.revoke_token(token.jti)
        token.hard_delete()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    print("create_user_profile")
    print(instance)
