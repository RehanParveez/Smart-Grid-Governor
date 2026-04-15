from rest_framework import viewsets
from metering.serializers.detail import MeterReadingSerializer, LossAbnormalitySerializer
from metering.models import LossAbnormality
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import action
from metering.services import EnergyAuditService
from rest_framework.response import Response
from smart_grid_governor.core.permissions import ZoneManagerPermission

class MeteringViewSet(viewsets.ModelViewSet):
  serializer_class = LossAbnormalitySerializer
  queryset = LossAbnormality.objects.all()
  authentication_classes = [JWTAuthentication]
  permission_classes = [ZoneManagerPermission]
  
  def get_queryset(self):
    user = self.request.user 
    if user.control == 'admin':
      return LossAbnormality.objects.all()
    if user.zone:
      subs_cases = self.queryset.filter(substation__zone=user.zone)
      feeder_cases = self.queryset.filter(feeder__substation__zone=user.zone)
      trans_cases = self.queryset.filter(transformer__feeder__substation__zone=user.zone)
      return (subs_cases | feeder_cases | trans_cases).distinct()

    return LossAbnormality.objects.none()

  @action(detail=False, methods=['post'])
  def submit_reading(self, request):
    serializer = MeterReadingSerializer(data=request.data)
    if serializer.is_valid():
      reading = serializer.save()   
      EnergyAuditService.detect_loss(reading.meter.branch, reading)
            
      return Response({'msg': 'the reading is recor.'}, status=201)
    return Response(serializer.errors, status=400)

  @action(detail=False, methods=['get'])
  def active_abnorms(self, request):
    active = LossAbnormality.objects.filter(is_verified=False).order_by('-severity')
    serializer = self.get_serializer(active, many=True)
    return Response(serializer.data)

  @action(detail=True, methods=['post'])
  def verify_theft(self, request, pk=None):
    abnormality = self.get_object()
    abnormality.is_verified = True
    abnormality.save()
    return Response({'msg': f'case {pk} verif by officer.'})
