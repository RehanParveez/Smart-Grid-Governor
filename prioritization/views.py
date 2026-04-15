from rest_framework import viewsets
from prioritization.serializers.detail import PriorityScoreSerializer, PriorWeightSerializer
from prioritization.models import FeedPriorScore, PriorityWeight
from rest_framework.decorators import action
from rest_framework.response import Response
from topology.models import Grid
from prioritization.services import PriorityCalculationEngine
from smart_grid_governor.core.permissions import ZoneManagerPermission
from rest_framework_simplejwt.authentication import JWTAuthentication

class PrioritizationViewSet(viewsets.ReadOnlyModelViewSet):
  serializer_class = PriorityScoreSerializer
  queryset = FeedPriorScore.objects.all()
  permission_classes = [ZoneManagerPermission]
  authentication_classes = [JWTAuthentication]
  
  def get_queryset(self):
    user = self.request.user
    if user.control == 'admin':
      return self.queryset
    if user.zone:
      return self.queryset.filter(feeder__substation__zone=user.zone)
    return self.queryset.none()
    
  @action(detail=False, methods=['get'])
  def factors(self, request):
    weights = PriorityWeight.objects.all()
    serializer = PriorWeightSerializer(weights, many=True)
    return Response(serializer.data)

  @action(detail=False, methods=['post'])
  def update_factors(self, request):
    user = request.user
    if user.control != 'admin':
      return Response({'err': 'the admin can change this'}, status=403)

    name = request.data.get('factor_name')
    val = request.data.get('weight_value')

    if not name:
      return Response({'err': 'factor_name is missing'}, status=400)
    if val is None:
      return Response({'err': 'weight_value is missing'}, status=400)
        
    new_data = {'weight_value': val}
    obj, created = PriorityWeight.objects.update_or_create(factor_name=name, defaults=new_data)
    msg = 'the factor was upd'
    if created:
      msg = 'the new factor was crea'

    weights = PriorityWeight.objects.all()
    serializer = PriorWeightSerializer(weights, many=True)
    return Response({'msg': msg, 'current_policy': serializer.data})

  @action(detail=False, methods=['post'])
  def recalculate(self, request):
    if request.user.control not in ['admin', 'engineer']:
      return Response({'err': 'no perm to trigger recal.'}, status=403)

    zone_id = request.data.get('zone_id')
    if not zone_id:
      return Response({'err': 'the zone_id is need.'}, status=400)
    zone = Grid.objects.filter(id=zone_id).first()
    if not zone:
      return Response({'err': 'the zone is not pres.'}, status=404)

    if request.user.control != 'admin':
      if zone != request.user.zone:
        return Response({'err': 'cant recal the other zone.'}, status=403)

    for substation in zone.substations.all():
      for feeder in substation.feeders.all():
        PriorityCalculationEngine.calc_score(feeder)
                
    PriorityCalculationEngine.upd_zone_ranks(zone)
    return Response({'msg': f'recal for {zone.name} done'})