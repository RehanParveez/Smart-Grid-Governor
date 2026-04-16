from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from scheduler.models import SheddingTarget, Cycle
from scheduler.serializers.detail import SheddingTargetSerializer, CycleSerializer
from scheduler.services import LoadSheddingOptimizer
from smart_grid_governor.core.permissions import ZoneManagerPermission
from rest_framework_simplejwt.authentication import JWTAuthentication

class SheddingTargetViewSet(viewsets.ModelViewSet):
  serializer_class = SheddingTargetSerializer
  queryset = SheddingTarget.objects.all()
  permission_classes = [ZoneManagerPermission]
  authentication_classes = [JWTAuthentication]
  
  def get_queryset(self):
    user = self.request.user
    if user.control == 'admin':
      return self.queryset
    return self.queryset.filter(zone=user.zone)
  
class CycleViewSet(viewsets.ModelViewSet):
  serializer_class = CycleSerializer
  queryset = Cycle.objects.all()
  permission_classes = [ZoneManagerPermission]
  authentication_classes = [JWTAuthentication]
  
  def get_queryset(self):
    user = self.request.user
    if user.control == 'admin':
      return self.queryset
    return self.queryset.filter(zone=user.zone)
    
  @action(detail=False, methods=['post'])
  def load_shed(self, request):
    target_id = request.data.get('target_id')
    tar = SheddingTarget.objects.filter(pk=target_id)
    tar = tar.first() 
    if not tar:
      return Response({'err': 'the tar is not pres.'}, status=404)
    
    if request.user.control == 'admin':
      pass     
    elif tar.zone != request.user.zone:
      return Response({'err': 'no acc is allow. to this zone'}, status=403)

    new_cycle = Cycle.objects.create(target=tar, zone=tar.zone, created_by=request.user, status = 'draft')
    service = LoadSheddingOptimizer()
    service.optim_plan(new_cycle)
    serializer = self.get_serializer(new_cycle)
    return Response(serializer.data, status=201)

  @action(detail=False, methods=['get'])
  def active_cycles(self, request):
    active = self.get_queryset().filter(status__in=['approved', 'executing'])
    serializer = self.get_serializer(active, many=True)
    return Response(serializer.data)

  @action(detail=True, methods=['post'])
  def approve(self, request, pk=None):
    cycle = self.get_object()
        
    if cycle.status == 'draft':
      cycle.status = 'approved'
      cycle.save()
      return Response({'msg': 'the cycle is appro.'}) 
    return Response({'err': 'this cycle cant be appro.'}, status=400)