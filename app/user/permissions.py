from rest_framework import permissions
import logging
logger = logging.getLogger('django')

class AllowAny(permissions.BasePermission):
    """
    Allows access only to authenticated users.
    """

    def has_permission(self, request, view):
        logger.info(f'method:{request.method} path: {request.path}')
        if request.data:
            logger.info(f'payload: {request.data}')
        if request.query_params:
            logger.info(f'params: {request.data}')
        return True
    

class AllowAnyWithoutLog(permissions.BasePermission):
    """
    Allows access only to authenticated users.
    """

    def has_permission(self, request, view):
        logger.info(f'method:{request.method} path: {request.path}')
        if request.query_params:
            logger.info(f'params: {request.data}')
        return True
        
