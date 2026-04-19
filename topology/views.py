from rest_framework import viewsets
from topology.serializers.detail import FeederSerializer, GridSerializer, BranchSerializer
from topology.models import Feeder, Grid, Branch
from smart_grid_governor.core.permissions import ZoneManagerPermission
from rest_framework.decorators import action
from topology.services import TopologyTreeService
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.core.cache import cache

class FeederViewSet(viewsets.ModelViewSet):
  serializer_class = FeederSerializer
  queryset = Feeder.objects.all()
  permission_classes = [ZoneManagerPermission]
  authentication_classes = [JWTAuthentication]
     
  def get_queryset(self):
    user = self.request.user
    if user.control == 'admin':
      return self.queryset
    
    cache_key = f'zone {user.zone.id} ids'
    feeder_ids = cache.get(cache_key)
    if feeder_ids is None:
      feeder_ids = list(self.queryset.filter(substation__zone=user.zone).values_list('id', flat=True))
      cache.set(cache_key, feeder_ids, 3600)
    
    return self.queryset.filter(id__in=feeder_ids)

  @action(detail=True, methods=['patch'])
  def toggle(self, request, pk=None):
    feeder = self.get_object() 
    upd_feeder = TopologyTreeService.feeder_power(feeder=feeder, requested_by=request.user)
    if upd_feeder == None:
      return Response({'err': 'denied'}, status=403)
            
    return Response({'status': 'status of electr power is upd'})

class GridViewSet(viewsets.ModelViewSet):
  serializer_class = GridSerializer
  queryset = Grid.objects.all()
  permission_classes = [ZoneManagerPermission] 
  authentication_classes = [JWTAuthentication]
    
  def get_queryset(self):
    user = self.request.user
    if user.control == 'admin':
      return self.queryset
    if user.zone != None:
      return self.queryset.filter(id=user.zone.id)
    return self.queryset.none()

  @action(detail=False, methods=['get'])
  def tree(self, request):
    user = self.request.user
    if user.control != 'admin':
      if user.zone == None:
        return Response({'err': 'no zone is assign.'}, status=403)
      zone_id = user.zone.id
    else:
      zone_id = request.query_params.get('zone_id')

    data = TopologyTreeService.recursive_structure(zone_id)
    return Response(data)

class BranchViewSet(viewsets.ModelViewSet):
  serializer_class = BranchSerializer
  queryset = Branch.objects.all()
  permission_classes = [ZoneManagerPermission]
  authentication_classes = [JWTAuthentication]

  def get_queryset(self):
    user = self.request.user
    if user.control == 'admin':
      return self.queryset
    return self.queryset.filter(transformer__feeder__substation__zone=user.zone)