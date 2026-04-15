from decimal import Decimal
from .models import PriorityWeight, FeedPriorScore
from economics.models import FeedFinanHealth
from metering.models import LossAbnormality

class PriorityCalculationEngine:
  @staticmethod
  def calc_score(feeder):
    all_weights = PriorityWeight.objects.all()
    weights_dict = {}
    for w in all_weights:
      weights_dict[w.factor_name] = w.weight_value

    w_recovery = weights_dict.get('recovery', Decimal('0.5'))
    w_theft = weights_dict.get('theft', Decimal('0.5'))

    health = FeedFinanHealth.objects.filter(feeder=feeder)
    health = health.first()
        
    recovery_val = Decimal('0.0')
    if health:
      recovery_val = health.reco_percent
    lat_loss = LossAbnormality.objects.filter(object_id=feeder.id, is_verified=False).order_by('-detected_at')
    lat_loss = lat_loss.first()
        
    loss_val = Decimal('0.0')
    if lat_loss:
      loss_val = lat_loss.loss_percentage
    theft_val = Decimal('100.0') - loss_val
    final_score = (recovery_val * w_recovery) + (theft_val * w_theft)
    score_obj, created = FeedPriorScore.objects.update_or_create(feeder=feeder, defaults={'final_score': final_score})
        
    return score_obj

  @staticmethod
  def upd_zone_ranks(zone):
    scores = FeedPriorScore.objects.filter(feeder__substation__zone=zone).order_by('-final_score')  
    current_rank = 1
    for score_record in scores:
      score_record.rank_in_zone = current_rank
      score_record.save()
      current_rank += 1