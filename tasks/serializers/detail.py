from rest_framework import serializers
from tasks.models import Maintenance, Investigation

class MaintenanceSerializer(serializers.ModelSerializer):
  investigation_id = serializers.ReadOnlyField(source = 'investigation_details.id')
  class Meta:
    model = Maintenance
    fields = ['subject', 'priority', 'status', 'created_at', 'investigation_id']

class EvidenceSerializer(serializers.ModelSerializer):
  class Meta:
    model = Investigation
    fields = ['evid_image', 'finding_notes']