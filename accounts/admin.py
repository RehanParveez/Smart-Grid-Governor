from django.contrib import admin
from accounts.models import User, AuditRecord

# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
  list_display = ['email', 'phone', 'dob', 'control', 'zone', 'created_at', 'updated_at']
  
@admin.register(AuditRecord)
class AuditRecordAdmin(admin.ModelAdmin):
  list_display = ['user', 'action', 'endpoint', 'ip_address', 'payload', 'created_at']
  

