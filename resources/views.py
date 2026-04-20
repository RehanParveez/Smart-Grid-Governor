from rest_framework import viewsets
from resources.serializers.detail import GenerationUnitSerializer, PowerSourceSerializer, FuelTypeSerializer
from resources.models import GenerationUnit, PowerSource, FuelType
from rest_framework.decorators import action
from resources.serializers.basic import GenerationUnitSerializer1
from rest_framework.response import Response
from resources.services import GenerationPlanner
from smart_grid_governor.core.permissions import ZoneManagerPermission
from rest_framework import permissions

class GenerationUnitViewSet(viewsets.ModelViewSet):
  serializer_class = GenerationUnitSerializer
  queryset = GenerationUnit.objects.all()
  permission_classes = [ZoneManagerPermission]
  
  def get_queryset(self):
    return GenerationUnit.objects.select_related('source', 'fuel_type', 'source__grid_zone').all()

  @action(detail=True, methods=['post'])
  def upd_output(self, request, pk=None):
    unit = self.get_object()
    serializer = GenerationUnitSerializer1(unit, data=request.data, partial=True)
    if serializer.is_valid():
      serializer.save()
      return Response({'msg': 'output is upd'}, status=200)
    return Response(serializer.errors, status=400)

  @action(detail=False, methods=['get'])
  def supply_status(self, request):
    stats = GenerationPlanner.total_supply()
    breakdown = GenerationPlanner.fuel_type_breakdown()
    return Response({'overall_stats': stats, 'fuel_mix': breakdown})

  @action(detail=False, methods=['get'])
  def fuel_costs(self, request):
    merit_order = GenerationPlanner.merit_order()
    serializer = self.get_serializer(merit_order, many=True)
    return Response(serializer.data)
  
class PowerSourceViewSet(viewsets.ModelViewSet):
  serializer_class = PowerSourceSerializer
  queryset = PowerSource.objects.all()
  permission_classes = [ZoneManagerPermission]

  def get_queryset(self):
    user = self.request.user
    if user.control == 'admin':
      return self.queryset
    return self.queryset.filter(grid_zone=user.zone)
      
class FuelTypeViewSet(viewsets.ModelViewSet):
  serializer_class = FuelTypeSerializer
  queryset = FuelType.objects.all()
  permission_classes = [ZoneManagerPermission]
  
  def get_permissions(self):
    if self.action in ['create', 'update', 'partial_update', 'destroy']:
      return [permissions.IsAdminUser()]
    return super().get_permissions()