from rest_framework import serializers
from economics.models import PaymentRec

class PaymentRecSerializer1(serializers.ModelSerializer):
  class Meta:
    model = PaymentRec
    fields = ['account', 'amount_paid']
    
