from rest_framework import serializers
from topology.models import Substation, Feeder, Transformer, Branch

class SubstationSerializer1(serializers.ModelSerializer):
  class Meta:
    model = Substation
    fields = ['zone', 'name']
    
class FeederSerializer1(serializers.ModelSerializer):
  class Meta:
    model = Feeder
    fields = ['substation', 'code', 'curr_load_mw']
    
class TransformerSerializer1(serializers.ModelSerializer):
  class Meta:
    model = Transformer
    fields = ['feeder', 'uid']
    
class BranchSerializer1(serializers.ModelSerializer):
  class Meta:
    model = Branch
    fields = ['transformer', 'account_number']
