from rest_framework import permissions
from .models import Target
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    
class IsAuthenticated(permissions.BasePermission):
    """
    Allows access only to authenticated users.
    """

    def has_permission(self, request, view):
        logging.info(">"*90)
        logging.info(f"A request was submitted by user {request.user.first_name} {request.user.last_name}, whose email address is {request.user.email}.")
        logging.info("<"*90)
        return bool(request.user and request.user.is_authenticated)
        
