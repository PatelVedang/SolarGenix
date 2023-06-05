from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from scanner.models import Target, TargetLog, Order, Tool

@receiver(post_save, sender=Target)
def target_scan_signal(sender, instance, created, **kwargs):
    if created:
        TargetLog.objects.create(target=Target(instance.id), action=1)
    else:
        if instance.is_deleted:
            TargetLog.objects.create(target=Target(instance.id), action=5)

@receiver(post_save, sender=Order)
def create_targets_signal(sender, instance, created, **kwargs):
    if created:
        tools = Tool.objects.filter(subscription_id=instance.subscrib.id)
        targets= []
        for tool in tools:
            targets.append(Target(ip=instance.target_ip, raw_result="", tool=tool, order=instance, scan_by = instance.client))
        Target.objects.bulk_create(targets)