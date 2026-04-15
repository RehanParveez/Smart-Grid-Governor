from django.db import models
from topology.models import Feeder

class PriorityWeight(models.Model):
  factor_name = models.CharField(max_length=70, unique=True)
  weight_value = models.DecimalField(max_digits=6, decimal_places=2)
  description = models.TextField(blank=True)

  def __str__(self):
    return f'{self.factor_name}'

class FeedPriorScore(models.Model):
  feeder = models.OneToOneField(Feeder, on_delete=models.CASCADE, related_name = 'priority_data')
  final_score = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
  rank_in_zone = models.PositiveIntegerField(null=True, blank=True)
  calculated_at = models.DateTimeField(auto_now=True)

  class Meta:
    ordering = ['-final_score']

  def __str__(self):
    return f'{self.feeder.code}'