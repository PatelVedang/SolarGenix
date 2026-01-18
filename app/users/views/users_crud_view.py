from auth_api.permissions import IsAuthenticated
from core.models import User
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from proj.base_view import BaseModelViewSet
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAdminUser
from users.constants import UserResponseConstants
from users.permission import CustomSuperAdminOrOwnerDeletePermission
from users.serializers import UserSerializer
from users.services import ExportUsersService
from utils.make_response import response
from utils.swagger import apply_swagger_tags


@apply_swagger_tags(
    tags=["Users"],
    extra_actions=["get_all"],
    method_details={
        "get_all": {
            "description": "Get all user records without pagination",
            "summary": "Get all users",
        },
    },
)
class UserViewSet(BaseModelViewSet):
    """
    A viewset for managing User objects with CRUD operations, custom permissions, and export functionality.

    Features:
    - Restricts access to user data based on authentication and user roles.
    - Superusers can view and create all users; regular users can only view their own data.
    - Custom permission for deleting users (superadmin or owner only).
    - Supports filtering users via query parameters.
    - Provides an endpoint to retrieve all users without pagination.
    - Allows exporting user data in CSV or JSON format with selectable fields (admin only).

    Endpoints:
    - list/retrieve/update/destroy: Standard DRF actions with custom permission logic.
    - create: Only superusers can create new users.
    - get_all: GET /users/get_all/ — Returns all users without pagination.
    - export_users: GET /users/export-users/ — Exports user data in CSV or JSON (admin only).

    Customizations:
    - get_permissions: Applies custom delete permission.
    - get_queryset: Filters queryset based on user role and query parameters.
    - create: Restricts creation to superusers.
    - get_all: Returns all users without pagination.
    - export_users: Exports user data with selectable fields and format.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        # Customize permissions based on the action
        if self.action == "destroy":
            return [
                CustomSuperAdminOrOwnerDeletePermission(),
            ]  # Replace with your custom permission class
        return super().get_permissions()

    def get_queryset(self):
        """
        Returns a queryset of User objects based on the requesting user's permissions.

        - If the requesting user is a superuser, returns all User objects.
        - Otherwise, returns only the User object corresponding to the requesting user.

        Returns:
            QuerySet: A Django QuerySet of User objects.
        """
        queryset = (
            User.objects.all()
            if self.request.user.is_superuser
            else User.objects.filter(id=self.request.user.id)
        )
        return queryset

    def create(self, request, *args, **kwargs):
        # Check if the user is a superuser
        if not request.user.is_superuser:
            raise PermissionDenied(UserResponseConstants.SUPERUSER_CAN_CREATE)

        # If superuser, proceed with the default create behavior
        return super().create(request, *args, **kwargs)

    @action(methods=["GET"], detail=False, url_path="get_all")
    def get_all(self, request, *args, **kwargs):
        """Get all user records without pagination."""
        self.pagination_class = None
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return response(
            data=serializer.data,
            message=self.get_message(request, *args, **kwargs),
            status_code=200,
        )

    @extend_schema(
        summary="Export Users Data",
        description="Export user data in CSV or JSON format using query parameters.",
        parameters=[
            OpenApiParameter(
                name="export_fields",
                description=(
                    "Comma-separated list of fields to export. "
                    f"Available: {', '.join([field.name for field in queryset.model._meta.get_fields() if field.concrete and not field.many_to_many and not field.one_to_many])}"
                ),
                required=False,
                type=OpenApiTypes.STR,
            ),
            OpenApiParameter(
                name="export_format",
                description="Format to export data",
                required=False,
                type=OpenApiTypes.STR,
                enum=["csv", "json"],
            ),
        ],
        # responses={200: UserExportSerializer(many=True)},
    )
    @action(
        methods=["GET"],
        detail=False,
        url_path="export-users",
        permission_classes=[IsAdminUser],
    )
    def export_users(self, request, *args, **kwargs):
        """Export user data in CSV or JSON format."""
        service = ExportUsersService()
        response_data = service.post_execute(request)

        return response_data
