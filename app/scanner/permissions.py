from rest_framework import permissions
from .models import Machine

class MachineRetrievePremission(permissions.BasePermission):
    def has_permission(self, request, view):
        result = True
        if request.method == 'POST':
            if request.data.get('machines_id'):
                if request.user.is_staff and request.user.is_superuser:
                    return True
                machines_id = request.data.get('machines_id')
                for machine_id in machines_id:
                    obj = Machine.objects.get(id=machine_id)
                    if obj.scan_by != request.user:
                        return False
            return result
        return result
    
    def has_object_permission(self, request, view, obj):
        if request.method == 'GET':
            if request.user.is_staff and request.user.is_superuser:
                return True
            return obj.scan_by == request.user
        
