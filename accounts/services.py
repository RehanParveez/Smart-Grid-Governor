from topology.models import Grid, Substation, Feeder, Transformer, Branch
from resources.models import GenerationUnit, PowerSource
from economics.models import BillingAcc, FeedFinanHealth
from metering.models import LossAbnormality

class AccessControlService:
  @staticmethod
  def zone_permission(user, node):
    if user.control == 'admin':
      return True
    if user.is_authenticated == False:
      return False

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
      target = node.branch

      if isinstance(target, Substation):
        if target.zone == user.zone:
          return True
      if isinstance(target, Feeder):
        if target.substation.zone == user.zone:
          return True
      if isinstance(target, Transformer):
        if target.feeder.substation.zone == user.zone:
          return True
    
    return False