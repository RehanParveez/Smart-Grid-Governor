from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from topology.models import Feeder
from topology.tasks import downstream_status
from django.core.cache import cache

@receiver(post_save, sender=Feeder)
def feeder_status(sender, instance, created, **kwargs):
    feeder_id = instance.id
    curr_status = instance.is_energized
    downstream_status.delay(feeder_id, curr_status)

@receiver([post_save, post_delete], sender=Feeder)
def invalid_feeder(sender, instance, **kwargs):
  zone_id = instance.substation.zone_id
  cache.delete(f'zone {zone_id} tree')
  cache.delete(f'zone {zone_id} ids')