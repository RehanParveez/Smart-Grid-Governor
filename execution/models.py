from django.db import models
from scheduler.models import LoadBalPlan
from topology.models import Feeder
from accounts.models import User

class GridWork(models.Model):
  WORK_KIND = (
    ('shed', 'Shed'),
    ('restore', 'Restore'),
   )
  STATUS_CHOICES = (
    ('sent', 'Sent'),
    ('confirmed', 'Confirmed'),
    ('failed', 'Failed'),
   )
  plan = models.ForeignKey(LoadBalPlan, on_delete=models.CASCADE, related_name = 'exec_work')
  feeder = models.ForeignKey(Feeder, on_delete=models.CASCADE, related_name = 'commands')
  work_kind = models.CharField(max_length=50, choices=WORK_KIND, default = 'shed')
  status = models.CharField(max_length=50, choices=STATUS_CHOICES, default = 'sent')
  created_at = models.DateTimeField(auto_now_add=True)
  confirmed_at = models.DateTimeField(null=True, blank=True)
    
  def __str__(self):
    return f'{self.work_kind}'

class HardwareFeedback(models.Model):
  work = models.OneToOneField(GridWork, on_delete=models.CASCADE, related_name = 'feedback_data')
  response_payload = models.JSONField() 
  delay_ms = models.PositiveIntegerField()
  created_at = models.DateTimeField(auto_now_add=True)
  load_at_feedback = models.DecimalField(max_digits=12, decimal_places=2)
  
  def __str__(self):
    return f'{self.work.id}'

class CancelRecord(models.Model):
  user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name = 'cancel')
  feeder = models.ForeignKey(Feeder, on_delete=models.CASCADE, related_name = 'manual_cancel')
  reason = models.TextField()
  dura_mins = models.PositiveIntegerField()
  created_at = models.DateTimeField(auto_now_add=True)
  emergency = models.BooleanField(default=False)

  def __str__(self):
    return f'{self.user.username}'