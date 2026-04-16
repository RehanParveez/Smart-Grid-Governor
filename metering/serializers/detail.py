from rest_framework import serializers
from metering.models import BranchMeter, MeterReading, LossAbnormality
from metering.serializers.basic import MeterReadingSerializer1

class BranchMeterSerializer(serializers.ModelSerializer):
  readings = MeterReadingSerializer1(many=True, read_only=True)
  class Meta:
    model = BranchMeter
    fields = ['meter_serial', 'is_active', 'readings']

class MeterReadingSerializer(serializers.ModelSerializer):
  class Meta:
    model = MeterReading
    fields = ['meter', 'energy_in_kwh', 'energy_out_kwh', 'created_at']

class LossAbnormalitySerializer(serializers.ModelSerializer):
  branch_name = serializers.StringRelatedField(source='branch', read_only=True)
  class Meta:
    model = LossAbnormality
    fields = ['branch_name', 'loss_percentage', 'severity', 'is_verified', 'detected_at']