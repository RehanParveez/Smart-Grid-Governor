from rest_framework import serializers
from topology.models import Grid, Substation, Feeder, Transformer, Branch

class GridSerializer(serializers.ModelSerializer):
  class Meta:
    model = Grid
    fields = ['name', 'description']

class SubstationSerializer(serializers.ModelSerializer):
  class Meta:
    model = Substation
    fields = ['zone', 'name', 'max_capa_mw', 'is_active']
    
class FeederSerializer(serializers.ModelSerializer):
  class Meta:
    model = Feeder
    fields = ['substation', 'code', 'curr_load_mw', 'is_shedding_active', 'is_energized']
    
class TransformerSerializer(serializers.ModelSerializer):
  class Meta:
    model = Transformer
    fields = ['feeder', 'uid', 'kva_rating', 'is_energized']
    
class BranchSerializer(serializers.ModelSerializer):
  class Meta:
    model = Branch
    fields = ['transformer', 'account_number', 'type', 'is_energized']
