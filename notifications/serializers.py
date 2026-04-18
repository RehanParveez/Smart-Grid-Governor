from rest_framework import serializers
from notifications.models import Alert

class AlertSerializer(serializers.ModelSerializer):
  class Meta:
    model = Alert
    fields = ['user', 'account', 'kind', 'message', 'status', 'created_at', 'sent_at']