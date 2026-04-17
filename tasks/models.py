from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from responders.models import Team
from metering.models import LossAbnormality

class Maintenance(models.Model):
  PRIORITY_CHOICES = (
    ('low', 'Low'),
    ('medium', 'Medium'),
    ('high', 'High'),
    ('critical', 'Critical')
  )
  
  STATUS_CHOICES = (
    ('assigned', 'Assigned'),
    ('ongoing', 'Ongoing'),
    ('solved', 'Solved'),
    ('failed', 'Failed')
  )
  subject = models.CharField(max_length=70)
  content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
  object_id = models.PositiveIntegerField()
  branch = GenericForeignKey('content_type', 'object_id')
  assigned = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, related_name = 'tasks')
  priority = models.CharField(max_length=45, choices=PRIORITY_CHOICES, default = 'medium')
  status = models.CharField(max_length=45, choices=STATUS_CHOICES, default = 'assigned')
  created_at = models.DateTimeField(auto_now_add=True)
  resolved_at = models.DateTimeField(null=True, blank=True)

  def __str__(self):
    return f'{self.subject}'

class Investigation(models.Model):
  abnorma = models.OneToOneField(LossAbnormality, on_delete=models.CASCADE, related_name = 'investigation')
  task = models.OneToOneField(Maintenance, on_delete=models.CASCADE, related_name = 'investigation_details')
  evid_image = models.ImageField(upload_to = 'theft_evidence/', null=True, blank=True)
  finding_notes = models.TextField(blank=True)

  def __str__(self):
    return f'{self.abnorma.id}'