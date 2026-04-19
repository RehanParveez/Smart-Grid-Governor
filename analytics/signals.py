from django.db.models.signals import post_save
from django.dispatch import receiver
from economics.models import PaymentRec
from analytics.services import SustainabilityCheck, AnalyticsService
from economics.services import RevenueAnalyService
from economics.models import FeedFinanHealth
from django.db.models import Sum
from decimal import Decimal

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
    
    RevenueAnalyService.calc_feeder(feeder)
    stats = FeedFinanHealth.objects.filter(feeder__substation__zone=target_zone).aggregate(expec=Sum('tot_defecit'),
      collec=Sum('reco_percent'))
        
    AnalyticsService.upd_efficiency(target_zone, total_collected=stats['collec'] or Decimal('0.00'), 
      total_expected=stats['expec'] or Decimal('0.00'))