from rest_framework import viewsets
from metering.serializers.detail import MeterReadingSerializer, LossAbnormalitySerializer
from metering.models import LossAbnormality
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import action
from metering.services import EnergyAuditService
from rest_framework.response import Response
from smart_grid_governor.core.permissions import ZoneManagerPermission
from topology.models import Substation, Feeder, Transformer
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

class MeteringViewSet(viewsets.ModelViewSet):
  serializer_class = LossAbnormalitySerializer
  queryset = LossAbnormality.objects.all()
  authentication_classes = [JWTAuthentication]
  permission_classes = [ZoneManagerPermission]
  
  def get_queryset(self):
    user = self.request.user 
    if user.control == 'admin':
      return self.queryset
    if user.zone:
      sub_ids = Substation.objects.filter(zone=user.zone).values_list('id', flat=True)
      fdr_ids = Feeder.objects.filter(substation__zone=user.zone).values_list('id', flat=True)
      tr_ids = Transformer.objects.filter(feeder__substation__zone=user.zone).values_list('id', flat=True)
      sub_ct = ContentType.objects.get_for_model(Substation)
      fdr_ct = ContentType.objects.get_for_model(Feeder)
      tr_ct = ContentType.objects.get_for_model(Transformer)
      
      return self.queryset.filter(
         Q(content_type=sub_ct, object_id__in=sub_ids) |
         Q(content_type=fdr_ct, object_id__in=fdr_ids) |
         Q(content_type=tr_ct, object_id__in=tr_ids))

    return self.queryset.none()

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
