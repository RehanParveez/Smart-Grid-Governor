from django.contrib import admin
from execution.models import GridWork, HardwareFeedback, CancelRecord

# Register your models here.
@admin.register(GridWork)
class GridWorkAdmin(admin.ModelAdmin):
  list_display = ['plan', 'feeder', 'work_kind', 'status', 'created_at', 'confirmed_at']
  
@admin.register(HardwareFeedback)
class HardwareFeedbackAdmin(admin.ModelAdmin):
  list_display = ['work', 'response_payload', 'delay_ms', 'created_at', 'load_at_feedback']
  
@admin.register(CancelRecord)
class CancelRecordAdmin(admin.ModelAdmin):
  list_display = ['user', 'feeder', 'reason', 'dura_mins', 'created_at', 'emergency']
