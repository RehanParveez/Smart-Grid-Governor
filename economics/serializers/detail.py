from rest_framework import serializers
from economics.models import BillingAcc, PaymentRec, FeedFinanHealth
from economics.serializers.basic import PaymentRecSerializer1

class BillingAccSerializer(serializers.ModelSerializer):
  payments = PaymentRecSerializer1(many=True, read_only=True)
  class Meta:
    model = BillingAcc
    fields = ['user', 'branch', 'payments', 'balance', 'culprit']

class PaymentRecSerializer(serializers.ModelSerializer):
  class Meta:
    model = PaymentRec
    fields = ['account', 'amount_paid', 'date_paid', 'reference_id']
    
class FeedFinanHealthSerializer(serializers.ModelSerializer):
  feeder_code = serializers.CharField(source='feeder.code', read_only=True)
  class Meta:
    model = FeedFinanHealth
    fields = ['feeder', 'feeder_code', 'reco_percent', 'tot_defecit', 'updated_at']