from celery import shared_task
from topology.models import Feeder, Transformer, Branch
from accounts.models import User
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def downstream_status(feeder_id, is_energized):
  transformers = Transformer.objects.filter(feeder_id=feeder_id)
  transformers.update(is_energized=is_energized)
  transformer_ids = transformers.values_list('id', flat=True)
  branches = Branch.objects.filter(transformer_id__in=transformer_ids)
  branches.update(is_energized=is_energized)

  if is_energized == True:
    status_msg = 'RESTORED'
  else:
    status_msg = 'CUT'
  subject = 'Electricity Power' + status_msg
  message = 'The power status is upd: ' + status_msg

  feeder = Feeder.objects.get(id=feeder_id)
  substation = feeder.substation
  grid_zone = substation.zone 

  raw_emails = User.objects.filter(zone=grid_zone, control = 'consumer').values_list('email', flat=True)
  raw_emails = raw_emails.distinct()
  final_recipients = []
  for email in raw_emails:
    if email != "":
      if email != None:
        final_recipients.append(email)

  if len(final_recipients) > 0:
    send_mail(subject=subject, message=message, from_email=settings.EMAIL_HOST_USER, recipient_list=final_recipients,
      fail_silently=False)