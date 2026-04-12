from django.dispatch import receiver
from django.db.models.signals import post_save
from resources.models import GenerationUnit, GenerationRecord

@receiver(post_save, sender=GenerationUnit)
def record_generation(sender, instance, created, **kwargs):
  GenerationRecord.objects.create(unit=instance, output_mw=instance.curr_output_mw)