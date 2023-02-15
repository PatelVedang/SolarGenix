from rest_framework import permissions
from .models import Target

class MachineRetrievePremission(permissions.BasePermission):
    def has_permission(self, request, view):
        result = True
        if request.method == 'POST':
            if request.data.get('targets_id'):
                if request.user.is_staff and request.user.is_superuser:
                    return True
                targets_id = request.data.get('targets_id')
                for target_id in targets_id:
                    obj = Target.objects.get(id=target_id)
                    if obj.scan_by != request.user:
                        return False
            return result
        return result
    
    def has_object_permission(self, request, view, obj):
        if request.method == 'GET':
            if request.user.is_staff and request.user.is_superuser:
                return True
            return obj.scan_by == request.user
        return obj.scan_by == request.user

class IsAdminUserOrList(permissions.IsAdminUser):
    def has_permission(self, request, view):
        if request.method == 'GET':
            return True
        return super().has_permission(request, view)
        
