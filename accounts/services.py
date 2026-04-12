from topology.models import Grid, Substation, Feeder, Transformer, Branch

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
    return False