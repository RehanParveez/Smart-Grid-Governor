from django.db import models
from django.contrib.auth.models import AbstractUser
from topology.models import Grid

class BaseModel(models.Model):
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
    
  class Meta:
    abstract = True

CONTROL_CHOICES = (
  ('admin', 'Admin'),
  ('engineer', 'Engineer'),
  ('officer', 'Officer'),
  ('consumer', 'Consumer'),
)

class User(AbstractUser, BaseModel):
  email = models.EmailField(unique=True)
  phone = models.CharField(max_length=50)
  dob = models.DateField(null=True, blank=True)
  control = models.CharField(max_length=60, choices=CONTROL_CHOICES, default = 'consumer')
  zone = models.ForeignKey(Grid, on_delete=models.SET_NULL, null=True, blank=True, related_name = 'assigned_users')
    
  def __str__(self):
    return f'{self.username}'