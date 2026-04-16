from django.http import JsonResponse
from rest_framework_simplejwt.authentication import JWTAuthentication
from scheduler.models import Cycle

class GridLockdownMiddleware:
  def __init__(self, get_response):
    self.get_response = get_response

  def __call__(self, request):
    path = request.path
    
    if path.startswith('/tokenobtain/'):
        return self.get_response(request)
      
    if not request.user.is_authenticated:
      auth_res = JWTAuthentication().authenticate(request)
      if auth_res:
        request.user = auth_res[0]
        
    lockdown_active = False
    if request.user.is_authenticated:
      if request.user.zone:
        active_cycles = Cycle.objects.filter(zone=request.user.zone, status = 'executing')
        lockdown_active = active_cycles.exists()

    if lockdown_active == True:
      metering = '/metering/metering/submit_reading/' in path
      theft_check = '/verify_theft/' in path
      scheduler = '/scheduler/' in path
      execution_feedback = '/execution/hardware_callback/' in path
      execution_pending = '/execution/pending/' in path
      
      if metering:
        return self.get_response(request)
      if theft_check:
        return self.get_response(request)
      if scheduler:
        return self.get_response(request)
      if execution_feedback:
        return self.get_response(request)
      if execution_pending:
        return self.get_response(request)
      
      write_methods = ['POST', 'PATCH', 'PUT', 'DELETE']
            
      if request.method in write_methods:
        if request.user.is_authenticated:
          if request.user.control != 'admin':
            return JsonResponse(
              {'err': 'System Lockdown Active', 'message': 'The grid is curr under optim.'}, status=503)
        else:
          return JsonResponse({'err': 'authen is need.'}, status=401)

    resp = self.get_response(request)
    return resp