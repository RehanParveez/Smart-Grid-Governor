from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from metering.models import LossAbnormality, MeterReading
from django.core.cache import cache
from tasks.services import ShipService
from decimal import Decimal

@receiver(post_save, sender=LossAbnormality)
def critical_theft(sender, instance, created, **kwargs):
  if created:
    if instance.severity == 'high':
      print(f'the criti loss {instance.loss_percentage} at {instance.branch}') 
      cache.set('GRID_LOCKDOWN_ENABLED', True, 3600)
      ShipService.assign_theft_inv(instance)

@receiver(post_delete, sender=MeterReading)
def remove_load_on(sender, instance, **kwargs):
  branch = instance.meter.branch
  if hasattr(branch, 'transformer'):
    feeder = branch.transformer.feeder
    zone_id = feeder.substation.zone_id
        
    val_to_remove = float(instance.energy_in_kwh)
    f_key = f'feeder {feeder.id} load'
    cached_f = cache.get(f_key, float(feeder.curr_load_mw))
    new_f_load = max(0, cached_f - val_to_remove) 
    cache.set(f_key, new_f_load, 3600)

    z_key = f'zone {zone_id} demand'
    cached_z = cache.get(z_key)
    if cached_z is not None:
      new_z_load = max(0, float(cached_z) - val_to_remove)
      cache.set(z_key, new_z_load, 3600)

    feeder.curr_load_mw = Decimal(str(new_f_load))
    feeder.save(update_fields=['curr_load_mw'])