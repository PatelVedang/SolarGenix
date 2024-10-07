from rest_framework.permissions import BasePermission


class CustomSuperAdminOrOwnerDeletePermission(BasePermission):
    """
    Custom permission to allow superusers (admins) to delete any user object.
    Regular users can only delete their own user object.
    """

    def has_permission(self, request, view):
        # Allow access if the user is authenticated
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        # Allow superusers to delete any object
        if request.user.is_superuser:
            return True
        # Regular users can only delete their own object
        return request.user == obj
