from django.contrib import admin
from analytics.models import Efficiency, Sustainability, LoadPredict

# Register your models here.
@admin.register(Efficiency)
class EfficiencyAdmin(admin.ModelAdmin):
  list_display = ['zone', 'date', 'tot_mw_suppl', 'tot_rev_expec', 'tot_rev_collec', 'effic_ratio']
  
@admin.register(Sustainability)
class SustainabilityAdmin(admin.ModelAdmin):
  list_display = ['zone', 'created_at', 'curr_deficit', 'improv_rate', 'is_sustainable']
  
@admin.register(LoadPredict)
class LoadPredictAdmin(admin.ModelAdmin):
  list_display = ['zone', 'predi_date', 'predi_peak_dem_mw', 'predi_shortfall_mw', 'confi_score']