from rest_framework import permissions
from .models import Target
import logging
logger = logging.getLogger('django')

class ScannerRetrievePremission(permissions.BasePermission):
    def has_permission(self, request, view):
        result = True
        if request.method == 'POST':
            if request.data.get('targets_id'):
                # if request.user.is_staff and request.user.is_superuser:
                if request.user.role_id in [1,2]:
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
            # if request.user.is_staff and request.user.is_superuser:
            if request.user.role_id in [1,2]:
                return True
            return obj.scan_by == request.user
        return obj.scan_by == request.user


class IsAdminUserOrList(permissions.IsAdminUser):
    def has_permission(self, request, view):
        if request.method == 'GET':
            return True
        return super().has_permission(request, view)
    

class UserHasPermission(permissions.IsAdminUser):
    def has_permission(self, request, view):
        if request.user.role.target_access:
            return True
        else:
            return False
        
    def has_object_permission(self, request, view, obj):
        if request.user.role.target_access:
            return True
        else:
            return False


class IsAuthenticated(permissions.BasePermission):
    """
    Allows access only to authenticated users.
    """

    def has_permission(self, request, view):
        logger.info(f'method:{request.method} path: {request.path}')
        if request.data:
            logger.info(f'payload: {request.data}')
        if request.query_params:
            logger.info(f'params: {request.data}')
        return bool(request.user and request.user.is_authenticated)
        
