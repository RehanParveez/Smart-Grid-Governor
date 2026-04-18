from rest_framework import viewsets
from analytics.serializers import EfficiencySerializer, SustainabilitySerializer, LoadPredictSerializer
from analytics.models import Sustainability, Efficiency, LoadPredict
from smart_grid_governor.core.permissions import ZoneManagerPermission
from rest_framework_simplejwt.authentication import JWTAuthentication

class CircularDebtViewSet(viewsets.ReadOnlyModelViewSet):
  serializer_class = SustainabilitySerializer
  queryset = Sustainability.objects.all()
  permission_classes = [ZoneManagerPermission]
  authentication_classes = [JWTAuthentication]

  def get_queryset(self):
    queryset = self.queryset.order_by('-created_at')   
    zone_id = self.request.query_params.get('zone_id')
    if zone_id:
      queryset = queryset.filter(zone_id=zone_id)     
    return queryset

class EfficiencyViewSet(viewsets.ReadOnlyModelViewSet):
  serializer_class = EfficiencySerializer
  queryset = Efficiency.objects.all()
  permission_classes = [ZoneManagerPermission]
  authentication_classes = [JWTAuthentication]

  def get_queryset(self):
    queryset = self.queryset.order_by('-date')  
    zone_id = self.request.query_params.get('zone_id')
    if zone_id:
      queryset = queryset.filter(zone_id=zone_id)    
    return queryset

class LoadPredictViewSet(viewsets.ReadOnlyModelViewSet):
  serializer_class = LoadPredictSerializer
  queryset = LoadPredict.objects.all()
  permission_classes = [ZoneManagerPermission]
  authentication_classes = [JWTAuthentication]

  def get_queryset(self):
    queryset = self.queryset.order_by('-predi_date')
    zone_id = self.request.query_params.get('zone_id')
    if zone_id:
      queryset = queryset.filter(zone_id=zone_id)
    return queryset