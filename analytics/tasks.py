from celery import shared_task
from topology.models import Grid
from analytics.services import SustainabilityCheck, LoadForecaster
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def daily_analy():
  all_zones = Grid.objects.all()
  tot_zones = all_zones.count()
    
  for zone in all_zones:
    SustainabilityCheck.calc_debt(zone)
    LoadForecaster.predict(zone)
    
  email_subject = 'analytics'
  email_body = """
  analytics done.
  tot process. zones: {count}
  """.format(count=tot_zones)

  recipient = [settings.EMAIL_HOST_USER]
  send_mail(subject=email_subject, message=email_body, from_email=settings.DEFAULT_FROM_EMAIL,
    recipient_list=recipient, fail_silently=False)
    
  return 'analytics done'