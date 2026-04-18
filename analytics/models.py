from django.db import models
from topology.models import Grid

class Efficiency(models.Model):
  zone = models.ForeignKey(Grid, on_delete=models.CASCADE, related_name = 'perf_records')
  date = models.DateField(auto_now_add=True)
  tot_mw_suppl = models.DecimalField(max_digits=12, decimal_places=2)
  tot_rev_expec = models.DecimalField(max_digits=15, decimal_places=2)
  tot_rev_collec = models.DecimalField(max_digits=15, decimal_places=2)
  effic_ratio = models.DecimalField(max_digits=5, decimal_places=2)

  def __str__(self):
    return f'{self.zone.name}'

class Sustainability(models.Model):
  zone = models.ForeignKey(Grid, on_delete=models.CASCADE, related_name = 'sustain_stats')
  created_at = models.DateTimeField(auto_now_add=True)
  curr_deficit = models.DecimalField(max_digits=16, decimal_places=2)
  improv_rate = models.DecimalField(max_digits=9, decimal_places=2, default=0.0)
  is_sustainable = models.BooleanField(default=False)

  def __str__(self):
    return f'{self.zone.name}'

class LoadPredict(models.Model):
  zone = models.ForeignKey(Grid, on_delete=models.CASCADE, related_name = 'load_predicts')
  predi_date = models.DateField()
  predi_peak_dem_mw = models.DecimalField(max_digits=12, decimal_places=2)
  predi_shortfall_mw = models.DecimalField(max_digits=12, decimal_places=2)
  confi_score = models.IntegerField(default=80)

  def __str__(self):
    return f'{self.zone.name}'
