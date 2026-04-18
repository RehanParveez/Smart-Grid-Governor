from django.db import models
from accounts.models import User
from economics.models import BillingAcc

class Alert(models.Model):
  ALERT_TYPE = (
    ('shedding', 'Shedding'),  
    ('warning', 'Warning'),     
    ('payment', 'Payment'),    
    ('status', 'Status'),       
  )
    
  STATUS_CHOICES = (
    ('pending', 'Pending'),
    ('sent', 'Sent'),
    ('failed', 'Failed'),
  )
  user = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'alerts')
  account = models.ForeignKey(BillingAcc, on_delete=models.CASCADE, related_name = 'alerts')
  kind = models.CharField(max_length=50, choices=ALERT_TYPE)
  message = models.TextField(null=True, blank=True)
  status = models.CharField(max_length=50, choices=STATUS_CHOICES, default = 'pending')
  created_at = models.DateTimeField(auto_now_add=True)
  sent_at = models.DateTimeField(null=True, blank=True)

  def __str__(self):
    return self.user.username