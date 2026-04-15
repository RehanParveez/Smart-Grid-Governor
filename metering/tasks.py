from celery import shared_task
from metering.models import BranchMeter
from metering.services import EnergyAuditService
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def theft_search():
  meters = BranchMeter.objects.filter(is_active=True)
  processed_count = 0
  detected_abnorm = []

  for met in meters:
    lat_read = met.readings.order_by('-created_at')
    lat_read = lat_read.first()
    if lat_read:
      abnormality = EnergyAuditService.detect_loss(met.branch, lat_read)
      processed_count += 1
      if abnormality:
        info = f'{met.branch} loss {abnormality.loss_percentage} severity {abnormality.severity}'
        detected_abnorm.append(info)

  if detected_abnorm:
    issues = ". ".join(detected_abnorm)
    subject = 'grid metering alert'
    body = f'{processed_count}. issues {len(detected_abnorm)}. details {issues}.'

    send_mail(subject=subject, message=body, from_email=settings.EMAIL_HOST_USER, recipient_list=[settings.EMAIL_HOST_USER],
      fail_silently=False)

  return f'{processed_count}'