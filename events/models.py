from django.db import models
from topology.models import Grid
from accounts.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

class AuditRecord(models.Model):
  KIND_CHOICES = (
    ('stress', 'Stress'),
    ('theft', 'Theft'),
    ('work', 'Work'),
    ('economy', 'Economy'),
    ('command', 'Command'),
  )
  user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name = 'audit_records')
  action = models.CharField(max_length=90)
  endpoint = models.CharField(max_length=100)
  kind = models.CharField(max_length=50, choices=KIND_CHOICES, default = 'command')
  zone = models.ForeignKey(Grid, on_delete=models.SET_NULL, null=True, blank=True, related_name = 'audit_records')
  content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
  object_id = models.PositiveIntegerField(null=True, blank=True)
  target = GenericForeignKey('content_type', 'object_id')
  ip_address = models.GenericIPAddressField(null=True)
  payload = models.JSONField(null=True)
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return f'{self.user} {self.action} at {self.created_at}'