from celery import shared_task
from topology.models import Grid
from prioritization.services import PriorityCalculationEngine
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def global_prior_recal():
  all_zones = Grid.objects.all()
  zones_processed_text = ""

  for zone in all_zones:
    for substation in zone.substations.all():
      for feeder in substation.feeders.all():
        PriorityCalculationEngine.calc_score(feeder)
        
    PriorityCalculationEngine.upd_zone_ranks(zone)
    zones_processed_text = zones_processed_text + " - " + zone.name + " (Done) "

  email_subject = 'daily grid report'
  email_message = f"""
  status report:
  {zones_processed_text}

  """
    
  send_mail(subject=email_subject, message=email_message, from_email=settings.EMAIL_HOST_USER,
    recipient_list=[settings.EMAIL_HOST_USER], fail_silently=False)

  return 'the global refresh is compl'