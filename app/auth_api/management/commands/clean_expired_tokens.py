from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Token  # Adjust if your model is elsewhere

class Command(BaseCommand):
    help = "Delete all expired tokens from Token Model"

    def handle(self, *args, **kwargs):
        now = timezone.now()
        expired_tokens = Token.objects.filter(expire_at__lt=now)
        count = expired_tokens.count()
        expired_tokens.delete()
        
        self.stdout.write(self.style.SUCCESS(f"✅ Deleted {count} expired tokens."))
