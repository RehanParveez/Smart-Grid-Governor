from rest_framework import viewsets
from metering.serializers.detail import MeterReadingSerializer, LossAbnormalitySerializer, BranchMeterSerializer
from metering.models import LossAbnormality, BranchMeter
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import action
from metering.services import EnergyAuditService
from rest_framework.response import Response
from smart_grid_governor.core.permissions import ZoneManagerPermission
from smart_grid_governor.core.mixins import GFKFilterMixin

class MeteringViewSet(viewsets.ModelViewSet, GFKFilterMixin):
  serializer_class = LossAbnormalitySerializer
  queryset = LossAbnormality.objects.all()
  authentication_classes = [JWTAuthentication]
  permission_classes = [ZoneManagerPermission]
  
  def get_queryset(self):
    return self.zone_filt_query(self.queryset, self.request.user)

  @action(detail=False, methods=['post'])
  def submit_reading(self, request):
    serializer = MeterReadingSerializer(data=request.data)
    if serializer.is_valid():
      reading = serializer.save()   
      EnergyAuditService.upd_load(reading.meter, reading)
      EnergyAuditService.detect_loss(reading.meter.branch, reading)
            
      return Response({'msg': 'the reading is recor.'}, status=201)
    return Response(serializer.errors, status=400)

  @action(detail=False, methods=['get'])
  def active_abnorms(self, request):
    active = self.get_queryset().filter(is_verified=False).order_by('-severity')
    serializer = self.get_serializer(active, many=True)
    return Response(serializer.data)

  @action(detail=True, methods=['post'])
  def verify_theft(self, request, pk=None):
    abnormality = self.get_object()
    abnormality.is_verified = True
    abnormality.save()
    return Response({'msg': f'case {pk} verif by officer.'})

class BranchMeterViewSet(viewsets.ReadOnlyModelViewSet, GFKFilterMixin):
  serializer_class = BranchMeterSerializer
  queryset = BranchMeter.objects.all()
  authentication_classes = [JWTAuthentication]
  permission_classes = [ZoneManagerPermission]

  def get_queryset(self):
    return self.zone_filt_query(self.queryset, self.request.user)
