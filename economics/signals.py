from django.dispatch import receiver
from django.db.models.signals import post_save
from topology.models import Branch
from accounts.models import User
from economics.models import BillingAcc

@receiver(post_save, sender=Branch)
def billing(sender, instance, created, **kwargs):
  if created:
    user = User.objects.filter(username=instance.account_number)
    user = user.first()
        
    if user:
      BillingAcc.objects.get_or_create(user=user, branch=instance, defaults={'balance': 0.00})
      print(f'link with sovereign {instance.account_number}')
    else:
      print(f'{instance.account_number} no owner.')