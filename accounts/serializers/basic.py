from rest_framework import serializers
from accounts.models import User

class UserSerializer1(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ['email', 'username']
    