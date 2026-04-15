from django.http import JsonResponse
from rest_framework_simplejwt.authentication import JWTAuthentication

class EconomicsRoleMiddleware:
  def __init__(self, get_response):
    self.get_response = get_response

  def __call__(self, request):
    path = request.path
    if not path.startswith('/tokenobtain/'):
      auth_res = JWTAuthentication().authenticate(request)
      if auth_res:
        request.user = auth_res[0]

    if path.startswith('/economics/') or path.startswith('/prioritization/'):
      user = request.user
      if not user.is_authenticated:
        return JsonResponse({'err': 'authen is need.'}, status=401)

      restr_keywords = ['/health/', '/top_perfs/', '/sync_payms/', '/factors/', '/recalculate/']
            
      is_touching_restricted_area = False
      for word in restr_keywords:
        if word in path:
          is_touching_restricted_area = True

      if is_touching_restricted_area or user.control == 'consumer':
          user_role = getattr(user, 'control', None)  
          if user_role == 'consumer':
            return JsonResponse({'err': 'the role is not author.', 'message': 'the consu cant view data.'}, status=403)

    response = self.get_response(request)
    return response