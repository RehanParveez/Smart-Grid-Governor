from django.db import models
from topology.models import Grid
from accounts.models import User, BaseModel

class Team(BaseModel):
  name = models.CharField(max_length=70)
  zone = models.ForeignKey(Grid, on_delete=models.CASCADE, related_name = 'teams')
  leader = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, limit_choices_to = {'control': 'officer'})
  members = models.ManyToManyField(User, related_name = 'team_memberships')
  is_active = models.BooleanField(default=True)

  def __str__(self):
    return f'{self.name} {self.zone.name}'

class Capability(models.Model):
  SKILL_CHOICES = (
    ('theft', 'Theft'),
    ('repair', 'Repair'),
    ('meter', 'Metering'),
    ('emergency', 'Emergency')
  )
  team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name = 'capabilities')
  skill = models.CharField(max_length=50, choices=SKILL_CHOICES)

  def __str__(self):
    return f'{self.team.name}'
