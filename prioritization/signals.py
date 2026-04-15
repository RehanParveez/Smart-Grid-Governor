from django.dispatch import receiver
from django.db.models.signals import post_save
from economics.models import FeedFinanHealth
from prioritization.services import PriorityCalculationEngine
from metering.models import LossAbnormality
from topology.models import Feeder

@receiver(post_save, sender=FeedFinanHealth)
def score_upd_on_paym(sender, instance, **kwargs):
  PriorityCalculationEngine.calc_score(instance.feeder)
  zone = instance.feeder.substation.zone
  PriorityCalculationEngine.upd_zone_ranks(zone)

@receiver(post_save, sender=LossAbnormality)
def score_upd_on_theft(sender, instance, **kwargs):
  if isinstance(instance.branch, Feeder):
    PriorityCalculationEngine.calc_score(instance.branch)
    zone = instance.branch.substation.zone
    PriorityCalculationEngine.upd_zone_ranks(zone)