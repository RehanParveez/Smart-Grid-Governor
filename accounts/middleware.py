from accounts.models import AuditRecord

class SovereignAuditMiddleware:
  def __init__(self, get_response):
    self.get_response = get_response

  def __call__(self, request):
    resp = self.get_response(request)

    if request.method in ['POST', 'PATCH', 'PUT', 'DELETE']:
      if request.user.is_authenticated:     
        ip = request.META.get('REMOTE_ADDR')
        AuditRecord.objects.create(user=request.user, action=request.method, endpoint=request.path,
          ip_address=ip, payload=request.POST.dict() or None)

    return resp