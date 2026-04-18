from economics.models import FeedFinanHealth
from django.db.models import Sum
from decimal import Decimal
from analytics.models import Sustainability, LoadPredict
from django.utils import timezone
from datetime import timedelta
from resources.models import GenerationRecord

class SustainabilityCheck:
  @staticmethod
  def calc_debt(zone):
    res = FeedFinanHealth.objects.filter(feeder__substation__zone=zone).aggregate(total=Sum('tot_defecit'))
    tot_defic = res['total']
    if tot_defic is None:
      tot_defic = Decimal('0.00')

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