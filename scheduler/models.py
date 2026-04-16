from django.db import models
from accounts.models import BaseModel, User
from topology.models import Grid, Feeder

class SheddingTarget(BaseModel):
  zone = models.ForeignKey(Grid, on_delete=models.CASCADE, related_name = 'incoming_targets')
  needed_red_mw = models.DecimalField(max_digits=12, decimal_places=2)
  start_time = models.DateTimeField()
  expec_dura_mins = models.PositiveIntegerField()
  is_addressed = models.BooleanField(default=False)

  def __str__(self):
    return str(self.needed_red_mw)

class Cycle(BaseModel):
  STATUS_CHOICES = (
    ('draft', 'Draft'),
    ('approved', 'Approved'),
    ('executing', 'Executing'),
    ('completed', 'Completed'),
    ('cancelled', 'Cancelled'),
  )
  target = models.OneToOneField(SheddingTarget, on_delete=models.SET_NULL, null=True, related_name = 'cycle')
  created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name = 'scheduled_cycles')
  zone = models.ForeignKey(Grid, on_delete=models.CASCADE, related_name = 'cycles')
  status = models.CharField(max_length=50, choices=STATUS_CHOICES, default = 'draft')
  total_mw_saved = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
  def __str__(self):
    return self.status

class LoadBalPlan(models.Model):
  cycle = models.ForeignKey(Cycle, on_delete=models.CASCADE, related_name = 'plans')
  feeder = models.ForeignKey(Feeder, on_delete=models.CASCADE, related_name = 'shedding_plans')
  prior_at_exec = models.DecimalField(max_digits=12, decimal_places=2)
  rank_at_exec = models.PositiveIntegerField()
  planned_off_time = models.DateTimeField()
  planned_on_time = models.DateTimeField()
  is_executed = models.BooleanField(default=False)
  executed_at = models.DateTimeField(null=True, blank=True)

  def __str__(self):
    return f'{self.feeder.code}'