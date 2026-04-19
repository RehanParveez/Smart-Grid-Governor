from topology.models import Substation, Feeder, Transformer
from django.contrib.contenttypes.models import ContentType
from metering.models import BranchMeter, MeterReading, LossAbnormality
from django.db.models import Sum
from decimal import Decimal
from django.core.cache import cache

class EnergyAuditService:
  @staticmethod
  def detect_loss(bran, inflow_read):
    tot_inflow = inflow_read.energy_in_kwh
    children = None
        
    if isinstance(bran, Substation):
      children = bran.feeders.all()
    elif isinstance(bran, Feeder):
      children = bran.transformers.all()
    elif isinstance(bran, Transformer):
      children = bran.branches.all()
    if not children:
      return None
        
    child_model = children.model
    child_type = ContentType.objects.get_for_model(child_model)
    child_ids = children.values_list('id', flat=True)
    child_meters = BranchMeter.objects.filter(content_type=child_type, object_id__in=child_ids)
        
    child_meter_ids = child_meters.values_list('id', flat=True)

    rea_data = MeterReading.objects.filter(meter_id__in=child_meter_ids)
    res = rea_data.aggregate(total=Sum('energy_in_kwh'))
        
    tot_outflow = res['total']
    if tot_outflow is None:
      tot_outflow = Decimal('0.00')

    delta = tot_inflow - tot_outflow
        
    if tot_inflow > 0:
      loss_ratio = (delta / tot_inflow) * 100
      if loss_ratio > 10:
        severity = 'low'
        if loss_ratio > 25:
          severity = 'medium'
        if loss_ratio > 40:
          severity = 'high'
                
        new_abnor = LossAbnormality.objects.create(branch=bran, loss_percentage=loss_ratio, severity=severity)
        return new_abnor
                
    return None

  @staticmethod
  def upd_load(meter, new_read):
    branch = meter.branch
    
    if not hasattr(branch, 'transformer'):
        return None
    feeder = branch.transformer.feeder
    zone_id = feeder.substation.zone_id
    last_read = MeterReading.objects.filter(meter=meter).exclude(id=new_read.id).order_by('-created_at')
    last_read = last_read.first()
    
    if last_read:
      prev_val = last_read.energy_in_kwh
    else:
      prev_val = Decimal('0.00')
    change_in_energy = new_read.energy_in_kwh - prev_val
    delta = float(change_in_energy)

    f_key = f'feeder {feeder.id} load'
    z_key = f'zone {zone_id} demand'
    
    cached_f_val = cache.get(f_key, feeder.curr_load_mw)
    new_f_load = float(cached_f_val) + delta
    cache.set(f_key, new_f_load, 3600)

    z_demand = cache.get(z_key)
    if z_demand is not None:
      new_z_load = float(z_demand) + delta
      cache.set(z_key, new_z_load, 3600)

    feeder.curr_load_mw = Decimal(str(new_f_load))
    feeder.save(update_fields=['curr_load_mw'])