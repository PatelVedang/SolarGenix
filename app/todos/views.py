from utils.swagger import apply_swagger_tags
from utils.custom_filter import filter_model
from proj.base_view import BaseModelViewSet
from .models import Todo
from .serializers import TodoSerializer
from auth_api.permissions import IsAuthenticated


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
class TodoViewset(BaseModelViewSet):
    queryset = Todo.objects.all()
    serializer_class = TodoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        query_params = self.request.query_params
        if query_params:
            # Apply filtering based on query parameters
            return filter_model(query_params, queryset, Todo)
        return queryset

    # def destroy(self, request, *args, **kwargs):
    #     Todo.objects.delete()
    #     return super().destroy(request, *args, **kwargs)
