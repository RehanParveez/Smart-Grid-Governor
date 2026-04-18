from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from notifications.models import Alert
from notifications.serializers import AlertSerializer

class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
  serializer_class = AlertSerializer
  queryset = Alert.objects.all()
  permission_classes = [permissions.IsAuthenticated]
  
  def get_queryset(self):
    user = self.request.user
    if user.control == 'admin':
      return self.queryset.select_related('user', 'account')
    if user.control == 'consumer':
      return self.queryset.filter(user=user).select_related('account')
        
    staff_types = ['officer', 'engineer']
    if user.control in staff_types:
      if user.zone:
        return self.queryset.filter(user__zone=user.zone).select_related('user', 'account')
    return self.queryset.none()

  @action(detail=False, methods=['get'])
  def outbox(self, request):
    alerts = self.get_queryset().order_by('-created_at')
    serializer = self.get_serializer(alerts, many=True)
    return Response(serializer.data)
