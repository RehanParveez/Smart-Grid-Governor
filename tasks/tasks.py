from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from tasks.models import Maintenance
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def monitor_task():
  limit = timezone.now() - timedelta(hours=3)
  late_tasks = Maintenance.objects.filter(status = 'assigned', created_at__lt=limit)
    
  total = late_tasks.count()
  if total > 0:
    late_tasks.update(priority = 'critical')
    sub = f'{total} late tasks'
    msg = f'these criti tasks need immed check'
    
    send_mail(subject=sub, message=msg, from_email=settings.DEFAULT_FROM_EMAIL, recipient_list=[settings.EMAIL_HOST_USER],
      fail_silently=False)
        
    return f'{total} alerts'
  return 'no late tasks are pres.'