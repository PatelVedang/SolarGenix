from auth_api.models import User
from auth_api.permissions import IsAuthenticated
from proj.base_view import BaseModelViewSet
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from utils.custom_filter import filter_model
from utils.make_response import response
from utils.swagger import apply_swagger_tags

from .permission import CustomSuperAdminOrOwnerDeletePermission
from .serializers import UserSerializer


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
        queryset = (
            User.objects.all()
            if self.request.user.is_superuser
            else User.objects.filter(id=self.request.user.id)
        )
        query_params = self.request.query_params
        if query_params:
            # Apply filtering based on query parameters
            return filter_model(query_params, queryset, User)
        return queryset

    def create(self, request, *args, **kwargs):
        # Check if the user is a superuser
        if not request.user.is_superuser:
            raise PermissionDenied("Only superusers can create users.")

        # If superuser, proceed with the default create behavior
        return super().create(request, *args, **kwargs)

    @action(methods=["GET"], detail=False, url_path="get_all")
    def get_all(self, request, *args, **kwargs):
        self.pagination_class = None
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return response(
            data=serializer.data,
            message=self.get_message(request, *args, **kwargs),
            status_code=200,
        )
