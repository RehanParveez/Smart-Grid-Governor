from django.dispatch import receiver
from django.db.models.signals import post_save
from metering.models import LossAbnormality
from django.core.cache import cache

@receiver(post_save, sender=LossAbnormality)
def critical_theft(sender, instance, created, **kwargs):
  if created:
    if instance.severity == 'high':
      print(f'the criti loss {instance.loss_percentage} at {instance.branch}') 
      cache.set('GRID_LOCKDOWN_ENABLED', True, 3600)