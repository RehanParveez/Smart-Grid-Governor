from accounts.models import AuditRecord
from rest_framework_simplejwt.authentication import JWTAuthentication

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
        AuditRecord.objects.create(user=request.user, action=request.method, endpoint=request.path,
          ip_address=ip, payload=request.POST.dict() or None)

    return resp