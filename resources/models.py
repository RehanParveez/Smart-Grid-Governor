from django.db import models
from accounts.models import BaseModel
from topology.models import Grid      

class FuelType(BaseModel):
  name = models.CharField(max_length=60, unique=True) 
  renewable = models.BooleanField(default=False)

  def __str__(self):
    return self.name

class PowerSource(BaseModel):
  OWNER_CHOICES = (
    ('state', 'State'),
    ('private', 'Private'),
  )
  name = models.CharField(max_length=70, unique=True)
  location = models.CharField(max_length=70)
  owner_type = models.CharField(max_length=60, choices=OWNER_CHOICES, default = 'state')
  grid_zone = models.ForeignKey(Grid, on_delete=models.SET_NULL, null=True, blank=True, 
    related_name = 'power_sources')

  def __str__(self):
    return self.name

class GenerationUnit(BaseModel):
  source = models.ForeignKey(PowerSource, on_delete=models.CASCADE, related_name = 'units')
  fuel_type = models.ForeignKey(FuelType, on_delete=models.PROTECT, related_name = 'units')
  unit_name = models.CharField(max_length=70)   
  installed_capacity_mw = models.DecimalField(max_digits=12, decimal_places=2)
  curr_output_mw = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
  cost_per_unit = models.DecimalField(max_digits=12, decimal_places=2)
  operational = models.BooleanField(default=True)

  def __str__(self):
    return f'{self.source.name} {self.unit_name}'

class GenerationRecord(models.Model):
  unit = models.ForeignKey(GenerationUnit, on_delete=models.CASCADE, related_name = 'records')
  output_mw = models.DecimalField(max_digits=12, decimal_places=2)
  recorded_at = models.DateTimeField(auto_now_add=True)

  class Meta:
    ordering = ['-recorded_at']

  def __str__(self):
    return f'{self.unit.unit_name} record at {self.recorded_at}'
