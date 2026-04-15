from rest_framework import serializers
from prioritization.models import PriorityWeight, FeedPriorScore

class PriorWeightSerializer(serializers.ModelSerializer):
  class Meta:
    model = PriorityWeight
    fields = ['factor_name', 'weight_value', 'description']

class PriorityScoreSerializer(serializers.ModelSerializer):
  feeder_code = serializers.CharField(source='feeder.code', read_only=True)
  zone_name = serializers.CharField(source='feeder.substation.zone.name', read_only=True)
  class Meta:
    model = FeedPriorScore
    fields = ['feeder_code', 'zone_name', 'final_score', 'rank_in_zone', 'calculated_at']