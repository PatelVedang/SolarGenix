from rest_framework import viewsets, status
from django.utils.text import capfirst
from utils.make_response import response as Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.decorators import action


class BaseModelViewSet(viewsets.ModelViewSet):
    http_method_names = ["get", "post", "patch", "delete"]
    response_message = ""
    status_code = ""

    def get_model_name(self):
        """
        Method to get the model name in a readable format.
        Override this method if you want a different model name representation.
        """
        return capfirst(self.queryset.model._meta.verbose_name)

    def get_message(self, request, *args, **kwargs):
        """
        Method to generate a dynamic message based on the request and model name.
        """
        model_name = self.get_model_name()
        if request.method == "POST":
            return f"{model_name} created successfully"
        elif request.method == "GET" and kwargs.get("pk", None):
            return f"{model_name} retrieved successfully"
        elif request.method == "GET":
            return f"List of {model_name}s retrieved successfully"
        elif request.method == "PATCH":
            return f"{model_name} partially updated successfully"
        elif request.method == "DELETE":
            return f"{model_name} deleted successfully"
        return "Request processed successfully"

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response(
            data=response.data,
            message=self.get_message(request, *args, **kwargs),
            status_code=status.HTTP_201_CREATED,
            headers=response.headers,
        )

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "fields",
                openapi.IN_QUERY,
                description="Comma separated fields",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                name="sort",
                in_=openapi.IN_QUERY,
                description="Fields to sort",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                name="search",
                in_=openapi.IN_QUERY,
                description="Search term.",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                name="search_fields",
                in_=openapi.IN_QUERY,
                description="Fields on search ",
                type=openapi.TYPE_STRING,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        fields = request.query_params.get("fields")

        if fields:
            fields = tuple(field.strip() for field in fields.split(","))

        serializer = self.get_serializer(self.get_queryset(), many=True, fields=fields)
        return Response(
            data=serializer.data,
            message=self.get_message(request, *args, **kwargs),
            status_code=status.HTTP_200_OK,
        )

    @action(methods=["GET"], detail=False, url_path="all")
    def get_all(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(
            data=serializer.data,
            message=self.get_message(request, *args, **kwargs),
            status_code=status.HTTP_200_OK,
        )

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "fields",
                openapi.IN_QUERY,
                description="Comma separated fields",
                type=openapi.TYPE_STRING,
            )
        ]
    )
    def retrieve(self, request, *args, **kwargs):
        # Get the object from the database
        instance = self.get_object()

        # Get the fields parameter from the query parameters
        fields = request.query_params.get("fields")

        if fields:
            fields = tuple(field.strip() for field in fields.split(","))
        else:
            fields = None

        # Get the serializer with dynamic fields
        serializer = self.get_serializer(instance, fields=fields)

        # Return the response with the filtered data
        return Response(
            data=serializer.data,
            message=self.get_message(request, *args, **kwargs),
            status_code=status.HTTP_200_OK,
        )

    def partial_update(self, request, *args, **kwargs):
        response = super().partial_update(request, *args, **kwargs)
        return Response(
            data=response.data,
            message=self.get_message(request, *args, **kwargs),
            status_code=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response(
            message=self.get_message(request, *args, **kwargs),
            status_code=status.HTTP_204_NO_CONTENT,
        )
