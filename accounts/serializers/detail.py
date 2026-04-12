from rest_framework import serializers
from accounts.models import User

class UserSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ['email', 'username', 'password', 'phone', 'dob', 'control', 'zone']
    extra_kwargs = {'password': {'write_only': True}}
  
  def create(self, validated_data):
    user=User.objects.create_user(
    username=validated_data.get('username'),
    email=validated_data.get('email'),
    password=validated_data.get('password'),
    phone=validated_data.get('phone'),
    dob=validated_data.get('dob'),
    control=validated_data.get('control'),
    zone=validated_data.get('zone')
    )
    return user