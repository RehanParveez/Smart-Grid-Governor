from django.contrib import admin
from economics.models import BillingAcc, PaymentRec, FeedFinanHealth

# Register your models here.
@admin.register(BillingAcc)
class BillingAccAdmin(admin.ModelAdmin):
  list_display = ['user', 'branch', 'balance', 'culprit']
  
@admin.register(PaymentRec)
class PaymentRecAdmin(admin.ModelAdmin):
  list_display = ['account', 'amount_paid', 'date_paid', 'reference_id']
  
@admin.register(FeedFinanHealth)
class FeedFinanHealthAdmin(admin.ModelAdmin):
  list_display = ['feeder', 'reco_percent', 'tot_defecit', 'updated_at']