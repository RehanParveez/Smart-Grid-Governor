from rest_framework import serializers
from analytics.models import Efficiency, Sustainability, LoadPredict

class EfficiencySerializer(serializers.ModelSerializer):
  zone_name = serializers.ReadOnlyField(source='zone.name')
  class Meta:
    model = Efficiency
    fields = ['zone_name', 'date', 'tot_mw_suppl', 'tot_rev_expec', 'tot_rev_collec', 'effic_ratio']

class SustainabilitySerializer(serializers.ModelSerializer):
  zone_name = serializers.ReadOnlyField(source='zone.name')
  class Meta:
    model = Sustainability
    fields = ['zone_name', 'created_at', 'curr_deficit', 'improv_rate', 'is_sustainable']

class LoadPredictSerializer(serializers.ModelSerializer):
  zone_name = serializers.ReadOnlyField(source='zone.name')
  class Meta:
    model = LoadPredict
    fields = ['zone_name', 'predi_date', 'predi_peak_dem_mw', 'predi_shortfall_mw', 'confi_score']