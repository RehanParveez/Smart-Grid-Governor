from django.db import transaction
from topology.models import Branch, Transformer, Feeder
from responders.models import Team
from tasks.models import Maintenance, Investigation

class ShipService:
  @staticmethod
  @transaction.atomic
  def assign_theft_inv(abnorm):
    tar_branch = abnorm.branch
    zone = None

    if isinstance(tar_branch, Branch):
      zone = tar_branch.transformer.feeder.substation.zone
    elif isinstance(tar_branch, Transformer):
      zone = tar_branch.feeder.substation.zone
    elif isinstance(tar_branch, Feeder): 
      zone = tar_branch.substation.zone
    if not zone:
      return 'err: the branch is not link. to a valid grid zone'

    team = Team.objects.filter(zone=zone, is_active=True, capabilities__skill = 'theft')
    team = team.first()
    if not team:
      return f'no team avail. in {zone.name}'

    new_task = Maintenance.objects.create(subject=f'{abnorm.loss_percentage}% loss', content_type=abnorm.content_type,
      object_id=abnorm.object_id, assigned=team, priority = 'high', status = 'assigned')
    Investigation.objects.create(abnorma=abnorm, task=new_task, finding_notes = 'the ship is trigg.')

    return f'{team.name} is shipped'