from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from scanner.models import Target, TargetLog, Order, Tool
from django.conf import settings
import os
import zlib

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
            targets.append(Target(ip=instance.target_ip, raw_result=zlib.compress("".encode("utf-8")), tool=tool, order=instance, scan_by = instance.client))
        Target.objects.bulk_create(targets)


@receiver(pre_save, sender=Order)
def client_order_update(sender, instance, **kwargs):
    # Only on update method 
    if not instance._state.adding:
        old_order = Order.objects.get(id=instance.id)
        new_order = instance

        if old_order.company_logo and new_order.company_logo and old_order.company_logo != new_order.company_logo:
            logo_path= f'{settings.MEDIA_ROOT}{str(old_order.company_logo)}'

            if os.path.exists(logo_path):
                if os.path.isfile(logo_path):
                    os.remove(logo_path)
