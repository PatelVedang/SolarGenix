from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from scanner.models import Target, TargetLog


@receiver(post_save, sender=Target)
def target_scan_signal(sender, instance, created, **kwargs):
    if created:
        TargetLog.objects.create(target=Target(instance.id), action=1)
    else:
        if instance.is_deleted:
            TargetLog.objects.create(target=Target(instance.id), action=5)
