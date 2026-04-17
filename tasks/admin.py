from django.contrib import admin
from tasks.models import Maintenance, Investigation

# Register your models here.
@admin.register(Maintenance)
class MaintenanceAdmin(admin.ModelAdmin):
  list_display = ['subject', 'content_type', 'object_id', 'branch', 'assigned', 'priority', 'status', 'created_at', 'resolved_at']

@admin.register(Investigation)
class InvestigationAdmin(admin.ModelAdmin):
  list_display = ['abnorma', 'task', 'evid_image', 'finding_notes']
  
  
