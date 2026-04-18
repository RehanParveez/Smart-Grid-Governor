from rest_framework import serializers
from events.models import AuditRecord

class AuditRecordSerializer(serializers.ModelSerializer):
  user_name = serializers.ReadOnlyField(source='user.username')
  zone_name = serializers.ReadOnlyField(source='zone.name')
  class Meta:
    model = AuditRecord
    fields = ['user_name', 'zone_name', 'action', 'endpoint', 'kind', 'ip_address', 'payload', 'created_at']
    read_only_fields = ['created_at', 'payload']