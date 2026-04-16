from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from execution.models import GridWork
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def old_commands():
  threshold = timezone.now() - timedelta(minutes=2)
  old_works = GridWork.objects.filter(status = 'sent', created_at__lt=threshold)
  if not old_works.exists():
    return 'no old comma det.'

  feeder_list = ""
  for work in old_works:
    work.status = 'failed'
    work.save()
    feeder_list = feeder_list + " * feeder code: " + str(work.feeder.code)
    feeder_list = feeder_list + " (Work ID: " + str(work.id) + ") "
    print('timeout on ' + str(work.feeder.code))

  subject = 'grid execution timeout'
    
  line1 = 'the feeders failed to respond'
  line2 = 'the list of feeders: ' + feeder_list
  line3 = 'kindly check the hard. conn & recs immed.'
    
  full_message = line1 + line2 + line3
    
  send_mail(subject, full_message, settings.EMAIL_HOST_USER, [settings.EMAIL_HOST_USER],
    fail_silently=False)
  
  return 'sent the email'