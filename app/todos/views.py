from proj.base_view import BaseModelViewSet
from rest_framework.decorators import action
from utils.custom_filter import filter_model
from utils.make_response import response
from utils.swagger import apply_swagger_tags

from .models import Todo
from .serializers import TodoSerializer


@apply_swagger_tags(
    tags=["Todos"],
    extra_actions=["get_all"],
    method_details={
        "get_all": {
            "operation_description": "Get all todos records without pagination",
            "operation_summary": "Get all todos",
        },
    },
)
class TodoViewSet(BaseModelViewSet):
    queryset = Todo.objects.all()
    serializer_class = TodoSerializer
    # permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        query_params = self.request.query_params
        if query_params:
            # Apply filtering based on query parameters
            return filter_model(query_params, queryset, Todo)
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
