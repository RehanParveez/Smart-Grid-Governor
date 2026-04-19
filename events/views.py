from rest_framework import viewsets
from events.serializers import AuditRecordSerializer
from events.models import AuditRecord
from smart_grid_governor.core.permissions import SovereignPermission, ZoneManagerPermission
from rest_framework.decorators import action
from rest_framework.response import Response
from smart_grid_governor.core.mixins import GFKFilterMixin

class EventViewSet(viewsets.ReadOnlyModelViewSet, GFKFilterMixin):
  serializer_class = AuditRecordSerializer
  queryset = AuditRecord.objects.all()
  permission_classes = [SovereignPermission]
  
  def get_queryset(self):
    user = self.request.user
    if user.control == 'admin':
      return self.queryset.all().select_related('user', 'zone') 
    if not user.zone:
      return self.queryset.none()
    
    direct_zone_recs = self.queryset.filter(zone=user.zone)
    gfk_filtered_recs = self.zone_filt_query(self.queryset, user)
    check_query = direct_zone_recs | gfk_filtered_recs
    ret_query = check_query.distinct()
    ret_query = ret_query.select_related('user', 'zone')
    return ret_query
    
  @action(detail=False, methods=['get'], permission_classes=[ZoneManagerPermission])
  def stream(self, request):
    criti_stream = self.get_queryset().filter(kind__in=['stress', 'theft']).order_by('-created_at')[:50]
    serializer = self.get_serializer(criti_stream, many=True)
    return Response(serializer.data)