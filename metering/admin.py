from django.contrib import admin
from metering.models import BranchMeter, MeterReading, LossAbnormality

# Register your models here.
@admin.register(BranchMeter)
class BranchMeterAdmin(admin.ModelAdmin):
  list_display = ['content_type', 'object_id', 'branch', 'meter_serial', 'is_active']
  
@admin.register(MeterReading)
class MeterReadingAdmin(admin.ModelAdmin):
  list_display = ['meter', 'energy_in_kwh', 'energy_out_kwh', 'created_at']
  
@admin.register(LossAbnormality)
class LossAbnormalityAdmin(admin.ModelAdmin):
  list_display = ['content_type', 'object_id', 'branch', 'loss_percentage', 'severity', 'is_verified', 'detected_at']
  