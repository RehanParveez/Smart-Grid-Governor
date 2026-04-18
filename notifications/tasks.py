from celery import shared_task
from notifications.models import Alert
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

@shared_task
def alert_delivery(alert_id):
  alert = Alert.objects.get(id=alert_id)
  user = alert.user  
  subject = f'{alert.get_kind_display()}'
  recipient_list = [user.email]
    
  send_mail(subject=subject, message=alert.message, from_email=settings.DEFAULT_FROM_EMAIL, recipient_list=recipient_list,
    fail_silently=False)   
  alert.status = 'sent'
  alert.sent_at = timezone.now()
  alert.save()
    
  print(f'sent to {user.email} id {alert_id}')