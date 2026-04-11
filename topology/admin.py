from django.contrib import admin
from topology.models import Grid, Substation, Feeder, Transformer, Branch

# Register your models here.
@admin.register(Grid)
class GridAdmin(admin.ModelAdmin):
  list_display = ['name', 'description']
  
@admin.register(Substation)
class SubstationAdmin(admin.ModelAdmin):
  list_display = ['zone', 'name', 'max_capa_mw', 'is_active']
  
@admin.register(Feeder)
class FeederAdmin(admin.ModelAdmin):
  list_display = ['substation', 'code', 'curr_load_mw', 'is_shedding_active', 'is_energized']
  
@admin.register(Transformer)
class TransformerAdmin(admin.ModelAdmin):
  list_display = ['feeder', 'uid', 'kva_rating', 'is_energized']
  
@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
  list_display = ['transformer', 'account_number', 'type', 'is_energized']
