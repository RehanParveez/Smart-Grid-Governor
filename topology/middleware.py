from django.http import JsonResponse
from django.core.cache import cache
from rest_framework_simplejwt.authentication import JWTAuthentication

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
    lockdown_active = cache.get('GRID_LOCKDOWN_ENABLED')

    if lockdown_active == True:
      if path.startswith('/metering/metering/submit_reading/') or '/verify_theft/' in path:
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