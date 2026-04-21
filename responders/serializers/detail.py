from rest_framework import serializers
from responders.models import Capability, Team

class CapabilitySerializer(serializers.ModelSerializer):
  class Meta:
    model = Capability
    fields = ['skill']

class TeamSerializer(serializers.ModelSerializer):
  capabilities = CapabilitySerializer(many=True, read_only=True)
  class Meta:
    model = Team
    fields = ['name', 'zone', 'capabilities', 'leader', 'members', 'is_active']
    extra_kwargs = {'zone': {'required': False}, 'members': {'allow_empty': True, 'required': False}}