from topology.models import Substation, Feeder, Transformer
from django.contrib.contenttypes.models import ContentType
from metering.models import BranchMeter, MeterReading, LossAbnormality
from django.db.models import Sum
from decimal import Decimal

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