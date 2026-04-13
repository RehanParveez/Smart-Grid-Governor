from django.db import models
from accounts.models import User
from topology.models import Branch, Feeder

class BillingAcc(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'billing_accounts')
  branch = models.OneToOneField(Branch, on_delete=models.CASCADE, related_name = 'billing_data')
  balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
  culprit = models.BooleanField(default=False)

  def __str__(self):
    return self.branch.account_number

class PaymentRec(models.Model):
  account = models.ForeignKey(BillingAcc, on_delete=models.CASCADE, related_name = 'payments')
  amount_paid = models.DecimalField(max_digits=12, decimal_places=2)
  date_paid = models.DateTimeField(auto_now_add=True)
  reference_id = models.CharField(max_length=60, unique=True)
  
  def __str__(self):
    return self.reference_id

class FeedFinanHealth(models.Model):
  feeder = models.OneToOneField(Feeder, on_delete=models.CASCADE, related_name = 'finan_health')
  reco_percent = models.DecimalField(max_digits=14, decimal_places=2, default=0.00)
  tot_defecit = models.DecimalField(max_digits=14, decimal_places=2, default=0.00)
  updated_at = models.DateTimeField(auto_now=True)
  
  def __str__(self):
    return self.feeder.code
