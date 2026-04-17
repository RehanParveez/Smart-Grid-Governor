from django.dispatch import receiver
from django.db.models.signals import post_save
from responders.models import Team
from tasks.models import Maintenance

@receiver(post_save, sender=Team)
def team_deactiv(sender, instance, **kwargs):
  if instance.is_active == False:
    Maintenance.objects.filter(assigned=instance, status = 'ongoing').update(status = 'assigned', assigned=None)