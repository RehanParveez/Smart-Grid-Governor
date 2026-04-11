from django.db import models

class Grid(models.Model):
  name = models.CharField(max_length=60, unique=True) 
  description = models.TextField(blank=True)

  def __str__(self):
    return self.name

class Substation(models.Model):
  zone = models.ForeignKey(Grid, on_delete=models.CASCADE, related_name = 'substations')
  name = models.CharField(max_length=70)
  max_capa_mw = models.DecimalField(max_digits=12, decimal_places=2)
  is_active = models.BooleanField(default=True)

  def __str__(self):
    return self.name

class Feeder(models.Model):
  substation = models.ForeignKey(Substation, on_delete=models.CASCADE, related_name = 'feeders')
  code = models.CharField(max_length=50, unique=True)
  curr_load_mw = models.DecimalField(max_digits=12, decimal_places=2)
  is_shedding_active = models.BooleanField(default=False)
  is_energized = models.BooleanField(default=True) 

  def __str__(self):
    return f'{self.code}'

class Transformer(models.Model):
  feeder = models.ForeignKey(Feeder, on_delete=models.CASCADE, related_name = 'transformers')
  uid = models.CharField(max_length=70, unique=True) 
  kva_rating = models.IntegerField()
  is_energized = models.BooleanField(default=True)

  def __str__(self):
    return f'{self.uid}'

class Branch(models.Model):
  TYPE_CHOICES = (
    ('residential', 'Residential'),
    ('industrial', 'Industrial'),
    ('important', 'Important'),
   )
  transformer = models.ForeignKey(Transformer, on_delete=models.CASCADE, related_name = 'branches')
  account_number = models.CharField(max_length=60, unique=True)
  type = models.CharField(max_length=60, choices=TYPE_CHOICES, default = 'residential')
  is_energized = models.BooleanField(default=True)

  def __str__(self):
    return f'{self.account_number}'
