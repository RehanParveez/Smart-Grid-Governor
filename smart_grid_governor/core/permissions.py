from rest_framework import permissions
from accounts.services import AccessControlService

class SovereignPermission(permissions.BasePermission):
  def has_permission(self, request, view):
    if request.user.is_authenticated == False:
      return False   
    if request.user.control == 'admin':
      return True
    else:
      return False

class ZoneManagerPermission(permissions.BasePermission):
  def has_permission(self, request, view):
    if request.user.is_authenticated == False:
      return False
    if request.user.control == 'admin':
      return True
    allowed_staff = ['engineer', 'officer']
    return request.user.control in allowed_staff
  
  def has_object_permission(self, request, view, obj):
    if request.user.control == 'admin':
      return True
    allowed_staff = ['engineer', 'officer']
    if request.user.control not in allowed_staff:
      return False
  
    access = AccessControlService.zone_permission(request.user, obj)  
    return access