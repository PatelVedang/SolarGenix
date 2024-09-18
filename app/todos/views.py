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
class TodoViewset(BaseModelViewSet):
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

    # def create(self, request, *args, **kwargs):
    #     serializer = self.serializer_class(data=request.data)
    #     if serializer.is_valid():
    #         # Process valid data
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     else:
    #         # Customize error response
    #         errors = []
    #         print("========", serializer.errors)
    #         for field, messages in serializer.errors.items():
    #             for message in messages:
    #                 expected_type = str(
    #                     serializer.fields[field].__class__.__name__
    #                 ).lower()
    #                 received_type = (
    #                     type(request.data.get(field)).__name__
    #                     if request.data.get(field) is not None
    #                     else "undefined"
    #                 )

    #                 error_detail = {
    #                     "code": "invalid_type",
    #                     "expected": expected_type,
    #                     "received": received_type,
    #                     "path": [field],
    #                     "message": message,
    #                 }
    #                 errors.append(error_detail)
    #         return Response(
    #             {"data": errors, "message": "validation error"},
    #             status=status.HTTP_422_UNPROCESSABLE_ENTITY,
    #         )
