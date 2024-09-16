from utils.custom_filter import filter_model

from proj.base_view import BaseModelViewSet
from auth_api.models import User
from .serializers import UserSerializer
from rest_framework.permissions import IsAuthenticated


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
