from django.contrib import admin
from scheduler.models import SheddingTarget, Cycle, LoadBalPlan

# Register your models here.
@admin.register(SheddingTarget)
class SheddingTargetAdmin(admin.ModelAdmin):
  list_display = ['zone', 'needed_red_mw', 'start_time', 'expec_dura_mins', 'is_addressed', 'created_at', 'updated_at']
  
@admin.register(Cycle)
class CycleAdmin(admin.ModelAdmin):
  list_display = ['target', 'created_by', 'zone', 'status', 'total_mw_saved', 'created_at', 'updated_at']

@admin.register(LoadBalPlan)
class LoadBalPlanAdmin(admin.ModelAdmin):
  list_display = ['cycle', 'feeder', 'prior_at_exec', 'rank_at_exec', 'planned_off_time', 'planned_on_time', 'is_executed', 'executed_at']