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

class AuditRecord(models.Model):
  user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name = 'audit_records')
  action = models.CharField(max_length=90)
  endpoint = models.CharField(max_length=100)
  ip_address = models.GenericIPAddressField(null=True)
  payload = models.JSONField(null=True)
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return f'{self.user} {self.action} at {self.created_at}'
