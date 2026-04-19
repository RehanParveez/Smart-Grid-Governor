from topology.models import Grid, Substation, Feeder, Transformer, Branch
from resources.models import GenerationUnit, PowerSource
from economics.models import BillingAcc, FeedFinanHealth
from metering.models import LossAbnormality, BranchMeter
from prioritization.models import FeedPriorScore
from scheduler.models import SheddingTarget, Cycle
from execution.models import GridWork, CancelRecord
from tasks.models import Maintenance
from responders.models import Team
from events.models import AuditRecord
from notifications.models import Alert

class AccessControlService:
  @staticmethod
  def zone_permission(user, node):
    if user is None:
      return False
    if user.is_authenticated == False:
      return False
    
    if user.control == 'admin':
      return True
    if user.zone == None:
      return False
    
    if isinstance(node, Grid):
      if node == user.zone:
          return True

    if isinstance(node, Substation):
      if node.zone == user.zone:
        return True

    if isinstance(node, Feeder):
      if node.substation.zone == user.zone:
        return True

    if isinstance(node, Transformer):
      if node.feeder.substation.zone == user.zone:
        return True

    if isinstance(node, Branch):
      if node.transformer.feeder.substation.zone == user.zone:
        return True
    
    if isinstance(node, GenerationUnit):
      if node.source.grid_zone == user.zone:
        return True
    if isinstance(node, PowerSource):
      if node.grid_zone == user.zone:
        return True
    
    if isinstance(node, BillingAcc):
      if node.branch.transformer.feeder.substation.zone == user.zone:
        return True
    if isinstance(node, FeedFinanHealth):
      if node.feeder.substation.zone == user.zone:
        return True
    
    if isinstance(node, LossAbnormality):
      return AccessControlService.check_gfk_jurisdiction(user, node.branch)
    
    if isinstance(node, BranchMeter):
      return AccessControlService.check_gfk_jurisdiction(user, node.branch)
  
    if isinstance(node, FeedPriorScore):
      if node.feeder.substation.zone == user.zone:
        return True
    
    if isinstance(node, SheddingTarget):
      if node.zone == user.zone:
        return True
    if isinstance(node, Cycle):
      if node.zone == user.zone:
        return True
    
    if isinstance(node, GridWork):
      if node.feeder.substation.zone == user.zone:
        return True
    if isinstance(node, CancelRecord):
      if node.feeder.substation.zone == user.zone:
        return True
    
    if isinstance(node, Maintenance):
      if node.assigned and node.assigned.zone == user.zone:
        return True
      return AccessControlService.check_gfk_jurisdiction(user, node.branch)
      
    if isinstance(node, Team):
      if node.zone == user.zone:
        return True
    
    if isinstance(node, AuditRecord):
      if node.zone == user.zone:
        return True
      return AccessControlService.check_gfk_jurisdiction(user, node.target)
            
    if isinstance(node, Alert):
      if node.user.zone == user.zone:
        return True
    
    return False
  
  @staticmethod
  def check_gfk_jurisdiction(user, target):
    if not target:
      return False
    if isinstance(target, Substation):
      return target.zone == user.zone  
    if isinstance(target, Feeder):
      return target.substation.zone == user.zone    
    if isinstance(target, Transformer):
      return target.feeder.substation.zone == user.zone    
    if isinstance(target, Branch):
      return target.transformer.feeder.substation.zone == user.zone
            
    return False
  
  