from decimal import Decimal
from economics.models import BillingAcc, PaymentRec, FeedFinanHealth
from django.db.models import Sum
from django.core.cache import cache

class RevenueAnalyService:
  @staticmethod
  def calc_feeder(feeder_instance):
    rate_per_mw = Decimal('150.00')
    load = feeder_instance.curr_load_mw
        
    target_rev = load * rate_per_mw
    accounts = BillingAcc.objects.filter(branch__transformer__feeder=feeder_instance)
    payment_data = PaymentRec.objects.filter(account__in=accounts)
    aggregation = payment_data.aggregate(total=Sum('amount_paid'))
        
    total_recov = aggregation['total']
    if total_recov is None:
      total_recov = Decimal('0.00')

    health, created = FeedFinanHealth.objects.get_or_create(feeder=feeder_instance)
        
    if target_rev > 0:
      ratio = total_recov / target_rev
      health.reco_percent = ratio * 100
    else:
      health.reco_percent = Decimal('0.00')

    health.tot_defecit = target_rev - total_recov 
    health.save()
    cache_key = f'feeder {feeder_instance.id} reco_perf'
    cache.set(cache_key, float(health.reco_percent), 86400)
    
    return health