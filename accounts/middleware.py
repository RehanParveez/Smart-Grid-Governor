from rest_framework_simplejwt.authentication import JWTAuthentication
from events.services import EventBus

class SovereignAuditMiddleware:
  def __init__(self, get_response):
    self.get_response = get_response

  def __call__(self, request):
    path = request.path
    if not request.user.is_authenticated:
      if not path.startswith('/tokenobtain/'):
        auth_res = JWTAuthentication().authenticate(request)
        if auth_res:
          request.user = auth_res[0]
    resp = self.get_response(request)

    if request.method in ['POST', 'PATCH', 'PUT', 'DELETE']:
      if request.user.is_authenticated:     
        ip = request.META.get('REMOTE_ADDR')
        data_payload = request.POST.dict()
        if not data_payload:
          data_payload = getattr(request, 'data', None)
        
        event_kind = 'command'
        if 'loss' in path:
          event_kind = 'theft'   
        if 'abnormality' in path:
          event_kind = 'theft'     
        if 'theft' in path:
          event_kind = 'theft'
        if 'stress' in path:
          event_kind = 'stress'      
        if 'shedding' in path:
          event_kind = 'stress'  
        if 'cycle' in path:
          event_kind = 'stress'
        if 'load' in path:
          event_kind = 'stress'   
        if 'recovery' in path:
          event_kind = 'stress'
        if 'billing' in path:
          event_kind = 'economy'      
        if 'payment' in path:
          event_kind = 'economy'      
        if 'revenue' in path:
          event_kind = 'economy'
        if 'maintenance' in path:
          event_kind = 'work'      
        if 'gridwork' in path:
          event_kind = 'work'      
        if 'task' in path:
          event_kind = 'work'

        EventBus.publish(kind=event_kind, zone=getattr(request.user, 'zone', None), actor=request.user,
          target=None, payload={'action': f'{request.method}_{path}', 'data': data_payload, 'ip': ip})

    return resp