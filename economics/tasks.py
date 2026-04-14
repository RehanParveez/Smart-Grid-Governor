from celery import shared_task
from topology.models import Feeder
from economics.services import RevenueAnalyService
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def grid_revenue():
  all_feeders = Feeder.objects.all()
  criti_feeders = []

  for feeder in all_feeders:
    health = RevenueAnalyService.calc_feeder(feeder)
    if health.reco_percent < 50:
      item = f' {feeder.code}  recov. {health.reco_percent}%'
      criti_feeders.append(item)

  if criti_feeders:
    report_text = ""
    for line in criti_feeders:
      report_text = report_text + line + " "

    subject = 'rev deficit'
    message = f"""
    these feeders are below the 50% limit:
    {report_text}
    
    """
    send_mail(subject=subject, message=message, from_email=settings.EMAIL_HOST_USER, recipient_list=[settings.EMAIL_HOST_USER],
      fail_silently=False)

  return 'the audit is process'