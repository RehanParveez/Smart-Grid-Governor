from rest_framework import serializers
from metering.models import MeterReading

class MeterReadingSerializer1(serializers.ModelSerializer):
  class Meta:
    model = MeterReading
    fields = ['meter', 'energy_in_kwh']
