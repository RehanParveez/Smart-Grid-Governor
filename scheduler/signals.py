from django.dispatch import receiver
from django.db.models.signals import post_save
from scheduler.models import Cycle
from scheduler.tasks import dispa_commands

@receiver(post_save, sender=Cycle)
def cycle_exec(sender, instance, created, **kwargs):
  if created:
    return
  if instance.status == 'approved':
    dispa_commands.delay(instance.id)