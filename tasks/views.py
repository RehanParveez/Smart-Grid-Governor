from rest_framework import viewsets
from tasks.serializers.detail import MaintenanceSerializer, EvidenceSerializer
from tasks.models import Maintenance
from rest_framework.decorators import action
from rest_framework.response import Response
from smart_grid_governor.core.permissions import ZoneManagerPermission
from rest_framework_simplejwt.authentication import JWTAuthentication

class TaskViewSet(viewsets.ModelViewSet):
  serializer_class = MaintenanceSerializer
  queryset = Maintenance.objects.all()
  permission_classes = [ZoneManagerPermission]
  authentication_classes = [JWTAuthentication]
  
  def get_queryset(self):
    user = self.request.user
    if user.control == 'admin':
      return self.queryset
    if user.zone:
      return self.queryset.filter(assigned__zone=user.zone)
        
    return self.queryset.none()

  @action(detail=False, methods=['get'])
  def my_tasks(self, request):
    user = self.request.user
    tasks = self.get_queryset().filter(assigned__members=user, status__in=['assigned', 'ongoing'])
    tasks = tasks.distinct()  
    serializer = self.get_serializer(tasks, many=True)
    return Response(serializer.data)

  @action(detail=True, methods=['patch'])
  def update_status(self, request, pk=None):
    task = self.get_object()
    new_status = request.data.get('status')
        
    if new_status in ['ongoing', 'solved', 'failed']:
      task.status = new_status
      task.save()
      return Response({'msg': f'task is now {new_status}'})
        
    return Response({'err': 'the wrong status'}, status=400)

  @action(detail=True, methods=['post'])
  def upload_evidence(self, request, pk=None):
    task = self.get_object()
    investigation = task.investigation_details
        
    serializer = EvidenceSerializer(investigation, data=request.data, partial=True)
    if serializer.is_valid():
      serializer.save()
      task.status = 'solved'
      task.save()
      return Response({'msg': 'the evid is saved & the task is solved'})       
    return Response(serializer.errors, status=400)