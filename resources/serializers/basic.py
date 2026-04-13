from rest_framework import serializers
from resources.models import FuelType, GenerationUnit

class FuelTypeSerializer1(serializers.ModelSerializer):
  class Meta:
    model = FuelType
    fields = ['id', 'name', 'renewable']

class GenerationUnitSerializer1(serializers.ModelSerializer):
  class Meta:
    model = GenerationUnit
    fields = ['unit_name', 'installed_capacity_mw']
