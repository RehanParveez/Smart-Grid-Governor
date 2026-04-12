from rest_framework import serializers
from resources.models import FuelType, GenerationUnit

class FuelTypeSerializer(serializers.ModelSerializer):
  class Meta:
    model = FuelType
    fields = ['name', 'renewable']

class GenerationUnitSerializer(serializers.ModelSerializer):
  fuel_name = serializers.ReadOnlyField(source = 'fuel_type.name')
  source_name = serializers.ReadOnlyField(source = 'source.name')
  class Meta:
    model = GenerationUnit
    fields = ['source_name', 'fuel_name', 'unit_name', 'installed_capacity_mw', 'curr_output_mw', 
      'cost_per_unit', 'operational']