from rest_framework import viewsets
from accounts.serializers.detail import UserSerializer
from accounts.models import User
from smart_grid_governor.core.permissions import SovereignPermission

class UserViewSet(viewsets.ModelViewSet):
  serializer_class = UserSerializer
  queryset = User.objects.all()
  permission_classes = [SovereignPermission]
    
  def get_queryset(self):
    user = self.request.user
    if user.control == 'admin':
      return self.queryset.select_related('zone')
    return self.queryset.none()
