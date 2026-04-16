from rest_framework import serializers
from topology.models import Grid, Substation, Feeder, Transformer, Branch
from topology.serializers.basic import BranchSerializer1, TransformerSerializer1, FeederSerializer1, SubstationSerializer1

class GridSerializer(serializers.ModelSerializer):
  substations = SubstationSerializer1(many=True, read_only=True)
  class Meta:
    model = Grid
    fields = ['name', 'description', 'substations']

class SubstationSerializer(serializers.ModelSerializer):
  feeders = FeederSerializer1(many=True, read_only=True)
  class Meta:
    model = Substation
    fields = ['zone', 'name', 'feeders', 'max_capa_mw', 'is_active']
    
class FeederSerializer(serializers.ModelSerializer):
  transformers = TransformerSerializer1(many=True, read_only=True)
  class Meta:
    model = Feeder
    fields = ['substation', 'code', 'transformers', 'curr_load_mw', 'is_shedding_active', 'is_energized']
    
class TransformerSerializer(serializers.ModelSerializer):
  branches = BranchSerializer1(many=True, read_only=True)
  class Meta:
    model = Transformer
    fields = ['feeder', 'uid', 'branches', 'kva_rating', 'is_energized']
    
class BranchSerializer(serializers.ModelSerializer):
  class Meta:
    model = Branch
    fields = ['transformer', 'account_number', 'type', 'is_energized']
