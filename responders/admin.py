from django.contrib import admin
from responders.models import Team, Capability

# Register your models here.
@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
  list_display = ['name', 'zone', 'leader', 'is_active', 'created_at', 'updated_at']
  
@admin.register(Capability)
class CapabilityAdmin(admin.ModelAdmin):
  list_display = ['team', 'skill']