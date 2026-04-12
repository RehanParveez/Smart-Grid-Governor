from django.db.models import Sum
from resources.models import GenerationUnit

class GenerationPlanner:
  @staticmethod
  def total_supply():
    stats = GenerationUnit.objects.filter(operational=True).aggregate(total_capacity=Sum('installed_capacity_mw'),
      total_actual_output=Sum('curr_output_mw'))
    return stats

  @staticmethod
  def merit_order():
    active_units = GenerationUnit.objects.filter(operational=True, curr_output_mw__gt=0
      ).order_by('cost_per_unit')
        
    return active_units

  @staticmethod
  def fuel_type_breakdown():
    breakdown = GenerationUnit.objects.values('fuel_type__name').annotate(total_mw=Sum('curr_output_mw')
      ).order_by('-total_mw')
    return breakdown