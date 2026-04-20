from rest_framework import serializers
from resources.models import FuelType, GenerationUnit, GenerationRecord

class FuelTypeSerializer1(serializers.ModelSerializer):
  class Meta:
    model = FuelType
    fields = ['id', 'name', 'renewable']

class GenerationUnitSerializer1(serializers.ModelSerializer):
  class Meta:
    model = GenerationUnit
    fields = ['unit_name', 'installed_capacity_mw', 'curr_output_mw']
    
class GenerationRecordSerializer1(serializers.ModelSerializer):
  class Meta:
    model = GenerationRecord
    fields = [['unit', 'output_mw', 'recorded_at']]
