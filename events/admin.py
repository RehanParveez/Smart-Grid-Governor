from django.contrib import admin
from events.models import AuditRecord

# Register your models here.
@admin.register(AuditRecord)
class AuditRecordAdmin(admin.ModelAdmin):
  list_display = ['user', 'action', 'endpoint', 'kind', 'zone', 'content_type', 'object_id', 'target', 'ip_address', 'payload', 'created_at']
