from rest_framework import viewsets
from economics.serializers.detail import FeedFinanHealthSerializer, PaymentRecSerializer
from economics.models import FeedFinanHealth, PaymentRec
from rest_framework.decorators import action
from topology.models import Feeder
from economics.services import RevenueAnalyService
from rest_framework.response import Response
from smart_grid_governor.core.permissions import ZoneManagerPermission
from rest_framework_simplejwt.authentication import JWTAuthentication

class EconomicsViewSet(viewsets.ModelViewSet):
  serializer_class = FeedFinanHealthSerializer
  queryset = FeedFinanHealth.objects.all()
  permission_classes = [ZoneManagerPermission]
  authentication_classes = [JWTAuthentication]
  
  def get_queryset(self):
    user = self.request.user
    if user.control == 'admin':
      return self.queryset
    if user.zone:
      return self.queryset.filter(feeder__substation__zone=user.zone)
        
    return self.queryset.none()
    
  @action(detail=False, methods=['get', 'patch'], url_path='feeder/(?P<feeder_id>[^/.]+)/health')
  def feeder_health(self, request, feeder_id=None):
    feeder = Feeder.objects.filter(pk=feeder_id)
    feeder = feeder.first()
        
    if feeder:
      health_record = RevenueAnalyService.calc_feeder(feeder)
      serializer = self.get_serializer(health_record)
      return Response(serializer.data)
        
    return Response({'err': 'feeder is not pres'}, status=404)

  @action(detail=False, methods=['get'])
  def top_perfs(self, request):
    top_data = self.get_queryset().order_by('-reco_percent')
    top = top_data[:10]
    serializer = self.get_serializer(top, many=True)
    return Response(serializer.data)

  @action(detail=False, methods=['post'])
  def sync_payms(self, request):
    incom_list = request.data
        
    if not isinstance(incom_list, list):
      return Response({'err': 'the list of payms is need.'}, status=400)
    counter = 0
    for payment in incom_list:
      serial = PaymentRecSerializer(data=payment)
            
      if serial.is_valid():
        serial.save()
        counter = counter + 1
    return Response({'msg': 'the sync is done', 'count': counter}, status=201)

class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
  queryset = PaymentRec.objects.all()
  serializer_class = PaymentRecSerializer
  permission_classes = [ZoneManagerPermission]
  authentication_classes = [JWTAuthentication]

  def get_queryset(self):
    user = self.request.user
    if user.control == 'admin':
      return self.queryset
    return self.queryset.filter(account__branch__transformer__feeder__substation__zone=user.zone)