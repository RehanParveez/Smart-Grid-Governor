from events.models import AuditRecord
from notifications.services import PublicTransparency

class EventBus:
  @staticmethod
  def publish(kind, zone, actor, target, payload):
    action_name = 'auto_system'
    if payload:
      if 'action' in payload:
        action_name = payload['action']

    event = AuditRecord.objects.create(kind=kind, zone=zone, user=actor, target=target, payload=payload,
      action=action_name)

    if kind == 'stress':
      PublicTransparency.grid_warning(zone, payload)
    if kind == 'theft':
      pass
    if kind == 'command':
      pass
        
    return event