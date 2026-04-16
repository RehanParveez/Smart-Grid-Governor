from rest_framework import viewsets
from accounts.serializers.detail import UserSerializer, AuditRecordSerializer
from accounts.models import User, AuditRecord
from smart_grid_governor.core.permissions import SovereignPermission
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import action
from rest_framework.response import Response

class UserViewSet(viewsets.ModelViewSet):
  serializer_class = UserSerializer
  queryset = User.objects.all()
  permission_classes = [SovereignPermission]
  authentication_classes = [JWTAuthentication]
  
  def get_queryset(self):
    user = self.request.user
    if user.control == 'admin':
      return self.queryset.select_related('zone')
    return self.queryset.none()
  
  @action(detail=False, methods=['get'])
  def audit_recs(self, request):
    if request.user.control != 'admin':
      return Response({'err': 'the access is not allow.', 'msg': 'the admins can only access'}, status=403)
    recs = AuditRecord.objects.all().select_related('user').order_by('-created_at')[:100]
    serializer = AuditRecordSerializer(recs, many=True)
    return Response(serializer.data)
