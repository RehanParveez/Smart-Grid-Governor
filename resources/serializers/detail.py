from rest_framework import serializers
from resources.models import FuelType, GenerationUnit, PowerSource
from resources.serializers.basic import GenerationRecordSerializer1, GenerationUnitSerializer1

class FuelTypeSerializer(serializers.ModelSerializer):
  class Meta:
    model = FuelType
    fields = ['name', 'renewable']

class GenerationUnitSerializer(serializers.ModelSerializer):
  fuel_name = serializers.ReadOnlyField(source = 'fuel_type.name')
  source_name = serializers.ReadOnlyField(source = 'source.name')
  records = GenerationRecordSerializer1(many=True, read_only=True)
  class Meta:
    model = GenerationUnit
    fields = ['source_name', 'fuel_name', 'unit_name', 'records', 'installed_capacity_mw', 'curr_output_mw', 
      'cost_per_unit', 'operational']

class PowerSourceSerializer(serializers.ModelSerializer):
  units = GenerationUnitSerializer1(many=True, read_only=True)
  class Meta:
    model = PowerSource
    fields = ['id', 'name', 'location', 'owner_type', 'units']
    