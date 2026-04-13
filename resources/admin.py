from django.contrib import admin
from resources.models import FuelType, PowerSource, GenerationUnit, GenerationRecord

# Register your models here.
@admin.register(FuelType)
class FuelTypeAdmin(admin.ModelAdmin):
  list_display = ['name', 'renewable', 'created_at', 'updated_at']
  
@admin.register(PowerSource)
class PowerSourceAdmin(admin.ModelAdmin):
  list_display = ['name', 'location', 'owner_type', 'grid_zone', 'created_at', 'updated_at']
  
@admin.register(GenerationUnit)
class GenerationUnitAdmin(admin.ModelAdmin):
  list_display = ['source', 'fuel_type', 'unit_name', 'installed_capacity_mw', 'curr_output_mw', 'cost_per_unit', 'operational', 'created_at', 'updated_at']
  
@admin.register(GenerationRecord)
class GenerationRecordAdmin(admin.ModelAdmin):
  list_display = ['unit', 'output_mw', 'recorded_at']
  


