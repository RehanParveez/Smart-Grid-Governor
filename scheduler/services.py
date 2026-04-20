from datetime import timedelta
from prioritization.models import FeedPriorScore
from scheduler.models import LoadBalPlan
from django.core.cache import cache

class LoadSheddingOptimizer:
  @staticmethod
  def optim_plan(cycle):
    if not cycle.target:
      return []

    target_mw = cycle.target.needed_red_mw
    zone = cycle.zone
    start_time = cycle.target.start_time
    duration = cycle.target.expec_dura_mins
        
    end_time = start_time + timedelta(minutes=duration)
    rankings = FeedPriorScore.objects.filter(feeder__substation__zone=zone).order_by('-rank_in_zone')

    current_saved_mw = 0
    plans_to_create = []
    for entry in rankings:
      if current_saved_mw >= target_mw:
        break
            
      feeder = entry.feeder
      f_key = f'feeder {feeder.id} load'
      live_f_load = cache.get(f_key, float(feeder.curr_load_mw))
      critical = feeder.transformers.filter(branches__type = 'important')
      critical = critical.exists()
      if critical:
        continue
      plan = LoadBalPlan(cycle=cycle, feeder=feeder, prior_at_exec=entry.final_score, rank_at_exec=entry.rank_in_zone, 
        planned_off_time=start_time, planned_on_time=end_time)
      plans_to_create.append(plan)
      current_saved_mw += live_f_load

    if plans_to_create:
      LoadBalPlan.objects.bulk_create(plans_to_create)
            
    cycle.total_mw_saved = current_saved_mw
    cycle.save(update_fields=['total_mw_saved'])
    return plans_to_create