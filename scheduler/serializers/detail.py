from rest_framework import serializers
from scheduler.models import SheddingTarget, LoadBalPlan, Cycle
from scheduler.serializers.basic import CycleSerializer1, LoadBalPlanSerializer1

class SheddingTargetSerializer(serializers.ModelSerializer):
  cycle = CycleSerializer1(read_only=True)
  class Meta:
    model = SheddingTarget
    fields = ['zone', 'needed_red_mw', 'cycle', 'start_time', 'expec_dura_mins', 'is_addressed']

class LoadBalPlanSerializer(serializers.ModelSerializer):
  feeder_code = serializers.CharField(source='feeder.code', read_only=True)
  class Meta:
     model = LoadBalPlan
     fields = ['feeder_code', 'prior_at_exec', 'rank_at_exec', 'planned_off_time', 'planned_on_time', 'is_executed']

class CycleSerializer(serializers.ModelSerializer):
  plans = LoadBalPlanSerializer1(many=True, read_only=True)
  class Meta:
     model = Cycle
     fields = ['target', 'plans' ,'zone', 'status', 'total_mw_saved']