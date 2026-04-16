from rest_framework import serializers
from scheduler.models import LoadBalPlan, Cycle

class LoadBalPlanSerializer1(serializers.ModelSerializer):
  feeder_code = serializers.CharField(source='feeder.code', read_only=True)
  class Meta:
     model = LoadBalPlan
     fields = ['feeder_code', 'prior_at_exec', 'rank_at_exec']

class CycleSerializer1(serializers.ModelSerializer):
  plans = LoadBalPlanSerializer1(many=True, read_only=True)
  class Meta:
     model = Cycle
     fields = ['target', 'plans' ,'zone']