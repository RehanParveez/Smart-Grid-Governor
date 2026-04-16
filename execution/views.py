from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from execution.models import GridWork, HardwareFeedback, CancelRecord
from execution.services import VerificationService
from execution.serializers.detail import GridWorkSerializer, CancelRecordSerializer
from smart_grid_governor.core.permissions import ZoneManagerPermission
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import permissions

class ExecutionViewSet(viewsets.ViewSet):
  queryset = GridWork.objects.all()
  authentication_classes = [JWTAuthentication]
  
  def get_permissions(self):
    if self.action == 'hardware_callback':
      return [permissions.IsAuthenticated()]
    return [ZoneManagerPermission()]

  def get_queryset(self):
    user = self.request.user
    if user.control == 'admin':
      return self.queryset
    if user.zone:
      return self.queryset.filter(feeder__substation__zone=user.zone)
    return self.queryset.none()
    
  @action(detail=False, methods=['post'])
  def hardware_callback(self, request):
    work_id = request.data.get('work_id')
    current_load = request.data.get('current_load')
    delay = request.data.get('delay_ms', 0)
        
    work = GridWork.objects.filter(pk=work_id)
    work = work.first()
    if not work:
      return Response({'err': 'the work_id is not pres.'}, status=404)

    feedback = HardwareFeedback.objects.create(work=work, response_payload=request.data, delay_ms=delay,
      load_at_feedback=current_load)

    work.status = 'confirmed'
    work.confirmed_at = timezone.now()
    work.save()

    feeder = work.feeder
    if work.work_kind == 'shed':
      feeder.is_energized = False
    else:
      feeder.is_energized = True
    feeder.save()

    verifier = VerificationService()
    verifier.verify_work(feedback.id)
    return Response({'msg': 'the feedback is proce. & verif.'})

  @action(detail=False, methods=['get'])
  def pending(self, request):
    pending_work = self.get_queryset().filter(status='sent')
    serializer = GridWorkSerializer(pending_work, many=True)
    return Response(serializer.data)

  @action(detail=False, methods=['get'])
  def cancel(self, request):
    user = self.request.user
    if user.control == 'admin':
      records = CancelRecord.objects.all()
    else:
      records = CancelRecord.objects.filter(feeder__substation__zone=user.zone)
      
    serializer = CancelRecordSerializer(records.order_by('-created_at'), many=True)
    return Response(serializer.data)

