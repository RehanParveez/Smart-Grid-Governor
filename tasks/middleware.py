from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.contenttypes.models import ContentType
from topology.models import Feeder
from tasks.models import Maintenance
from django.http import JsonResponse

class MaintenanceMiddleware:
  def __init__(self, get_response):
    self.get_response = get_response

  def __call__(self, request):
    path = request.path
    if not path.startswith('/tokenobtain/'):
      if not request.user.is_authenticated:
        auth_res = JWTAuthentication().authenticate(request)
        if auth_res:
          request.user = auth_res[0]
    
    if request.method == 'POST':
      if 'execution' in request.path:
        feeder_id = request.POST.get('feeder_id')
        if feeder_id:
          feeder_type = ContentType.objects.get_for_model(Feeder)
          active_work = Maintenance.objects.filter(content_type=feeder_type, object_id=feeder_id, status = 'ongoing')

          if active_work.exists():
            return JsonResponse({'err': 'the maintenance is ongoing', 'status': 'locked'}, status=403)

    return self.get_response(request)