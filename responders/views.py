from rest_framework import viewsets
from responders.serializers.detail import TeamSerializer
from responders.models import Team
from smart_grid_governor.core.permissions import ZoneManagerPermission

class TeamViewSet(viewsets.ModelViewSet):
  serializer_class = TeamSerializer
  queryset = Team.objects.all()
  permission_classes = [ZoneManagerPermission]

  def get_queryset(self):
    user = self.request.user
    if user.control == 'admin':
      return self.queryset
    if user.zone:
      return self.queryset.filter(zone=user.zone)  
    return self.queryset.none()

  def perform_create(self, serializer):
    if self.request.user.control != 'admin':
      serializer.save(zone=self.request.user.zone)
    else:
      serializer.save()
