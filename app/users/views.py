from auth_api.models import User
from proj.base_view import BaseModelViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from utils.custom_filter import filter_model
from utils.make_response import response
from utils.swagger import apply_swagger_tags

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
class UserViewset(BaseModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        query_params = self.request.query_params
        if query_params:
            # Apply filtering based on query parameters
            return filter_model(query_params, queryset, User)
        return queryset

    @action(methods=["GET"], detail=False, url_path="get_all")
    def get_all(self, request, *args, **kwargs):
        self.pagination_class = None
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return response(
            data=serializer.data,
            message=self.get_message(request, *args, **kwargs),
            status_code=200,
        )
