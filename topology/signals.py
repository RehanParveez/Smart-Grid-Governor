from django.dispatch import receiver
from django.db.models.signals import post_save
from topology.models import Feeder
from topology.tasks import downstream_status

@receiver(post_save, sender=Feeder)
def feeder_status(sender, instance, created, **kwargs):
    feeder_id = instance.id
    curr_status = instance.is_energized
    downstream_status.delay(feeder_id, curr_status)