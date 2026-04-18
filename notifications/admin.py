from django.contrib import admin
from notifications.models import Alert

# Register your models here.
@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
  list_display = ['user', 'account', 'kind', 'message', 'status', 'created_at', 'sent_at']

