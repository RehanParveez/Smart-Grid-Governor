from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

class BranchMeter(models.Model):
  content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
  object_id = models.PositiveIntegerField()
  branch = GenericForeignKey('content_type', 'object_id')
  meter_serial = models.CharField(max_length=60, unique=True)
  is_active = models.BooleanField(default=True)
  
  class Meta:
    indexes = [models.Index(fields=['content_type', 'object_id'])]

  def __str__(self):
    return f'{self.meter_serial}'

class MeterReading(models.Model):
  meter = models.ForeignKey(BranchMeter, on_delete=models.CASCADE, related_name = 'readings')
  energy_in_kwh = models.DecimalField(max_digits=12, decimal_places=2)
  energy_out_kwh = models.DecimalField(max_digits=12, decimal_places=2)
  created_at = models.DateTimeField(auto_now_add=True)
  
  def __str__(self):
    return f'{self.meter.meter_serial}'

class LossAbnormality(models.Model):
  SEVERITY_CHOICES = (
    ('low', 'Low'),
    ('medium', 'Medium'),
    ('high', 'High')
  )
  content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
  object_id = models.PositiveIntegerField()
  branch = GenericForeignKey('content_type', 'object_id')
  loss_percentage = models.DecimalField(max_digits=7, decimal_places=2)
  severity = models.CharField(max_length=50, choices=SEVERITY_CHOICES, default = 'low')
  is_verified = models.BooleanField(default=False)
  detected_at = models.DateTimeField(auto_now_add=True)
  
  class Meta:
    indexes = [models.Index(fields=['content_type', 'object_id'])]
  
  def __str__(self):
    return f'{self.loss_percentage} {self.severity.title()}'
