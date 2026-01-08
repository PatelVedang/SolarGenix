from utils.swagger import apply_swagger_tags
from utils.custom_filter import filter_model
from proj.base_view import BaseModelViewSet
from core.models import Todos
from todos.serializers import TodosSerializer
from auth_api.permissions import IsAuthenticated
from rest_framework.decorators import action
from utils.make_response import response

@apply_swagger_tags(
    tags=["Todos"],
    extra_actions=["get_all"],
    method_details={
        "get_all": {
            "description": "Get all Todos records without pagination",
            "summary": "Get all Todos",
        },
    },
)
class TodosViewSet(BaseModelViewSet):
    queryset = Todos.objects.all()
    serializer_class = TodosSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        query_params = self.request.query_params
        if query_params:
            # Apply filtering based on query parameters
            return filter_model(query_params, queryset, Todos)
        return queryset
    
    @action(methods=["GET"], detail=False, url_path="all")
    def get_all(self, request, *args, **kwargs):
        self.pagination_class = None
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return response(
            data=serializer.data,
            message=self.get_message(request, *args, **kwargs),
            status_code=200,
        )
