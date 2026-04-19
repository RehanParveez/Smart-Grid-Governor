from economics.models import FeedFinanHealth
from django.db.models import Sum
from decimal import Decimal
from analytics.models import Sustainability, LoadPredict, Efficiency
from django.utils import timezone
from datetime import timedelta
from resources.models import GenerationRecord
from django.core.cache import cache

class SustainabilityCheck:
  @staticmethod
  def calc_debt(zone):
    res = FeedFinanHealth.objects.filter(feeder__substation__zone=zone).aggregate(total=Sum('tot_defecit'))
    tot_defic = res['total']
    if tot_defic is None:
      tot_defic = Decimal('0.00')
    
    z_debt_key = f'zone {zone.id} deficit'
    cache.set(z_debt_key, float(tot_defic), 86400)

    last_rec = Sustainability.objects.filter(zone=zone).order_by('-created_at')
    last_rec = last_rec.first()
        
    improv_rate = Decimal('0.00')
    if last_rec:
      if last_rec.curr_deficit > 0:
        diff = last_rec.curr_deficit - tot_defic
        improv_rate = (diff / last_rec.curr_deficit) * 100

    is_sustainable = False
    if improv_rate > 0:
      is_sustainable = True

    return Sustainability.objects.create(zone=zone, curr_deficit=tot_defic, improv_rate=improv_rate, is_sustainable=is_sustainable)

class LoadForecaster:
  @staticmethod
  def predict(zone):
    tomorrow = timezone.now().date() + timedelta(days=1)
    res = GenerationRecord.objects.filter(unit__source__grid_zone=zone).aggregate(avg=Sum('output_mw'))
        
    avg_gen = res['avg']
    if avg_gen is None:
      avg_gen = Decimal('0.00')
        
    multiplier = Decimal('1.10')
    predic_demand = avg_gen * multiplier
    shortfall = predic_demand - avg_gen
    if shortfall < 0:
      shortfall = Decimal('0.00')

    return LoadPredict.objects.create(zone=zone, predi_date=tomorrow, predi_peak_dem_mw=predic_demand,
      predi_shortfall_mw=shortfall, confi_score=85)

class AnalyticsService:
  @staticmethod
  def upd_efficiency(zone, total_collected, total_expected):
    if total_expected > 0:
      ratio = (total_collected / total_expected) * 100
    else:
      ratio = Decimal('0.00')
            
    cache_key = f'zone {zone.id} efficiency'
    cache.set(cache_key, float(ratio), 86400)  
    capa_res = zone.substations.aggregate(total=Sum('max_capa_mw'))
    total_capacity = capa_res['total'] or Decimal('0.00')

    today = timezone.now().date()
    effic_rec, created = Efficiency.objects.update_or_create(zone=zone, date=today, defaults={
      'tot_rev_expec': total_expected, 'tot_rev_collec': total_collected, 'effic_ratio': ratio, 'tot_mw_suppl': total_capacity})
    return effic_rec