from rest_framework import serializers
from execution.models import GridWork, HardwareFeedback, CancelRecord

class GridWorkSerializer(serializers.ModelSerializer):
  feeder_code = serializers.CharField(source='feeder.code', read_only=True)
  class Meta:
    model = GridWork
    fields = ['plan', 'feeder', 'feeder_code', 'work_kind', 'status', 'created_at', 'confirmed_at']

class HardwareFeedbackSerializer(serializers.ModelSerializer):
  class Meta:
    model = HardwareFeedback
    fields = ['response_payload', 'delay_ms', 'created_at', 'load_at_feedback']

class CancelRecordSerializer(serializers.ModelSerializer):
  username = serializers.CharField(source='user.username', read_only=True)
  feeder_code = serializers.CharField(source='feeder.code', read_only=True)
  class Meta:
    model = CancelRecord
    fields = ['user', 'username', 'feeder', 'feeder_code', 'reason', 'dura_mins', 'created_at', 'emergency']