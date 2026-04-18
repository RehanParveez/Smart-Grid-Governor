from django.db.models.signals import post_save
from django.dispatch import receiver
from economics.models import PaymentRec
from analytics.services import SustainabilityCheck

@receiver(post_save, sender=PaymentRec)
def debt_on_paym(sender, instance, created, **kwargs):
  if created:
    billing_account = instance.account
    branch = billing_account.branch
    transformer = branch.transformer
    feeder = transformer.feeder
    substation = feeder.substation
    target_zone = substation.zone

    SustainabilityCheck.calc_debt(target_zone)