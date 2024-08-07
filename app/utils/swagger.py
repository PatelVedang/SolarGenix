from functools import wraps

from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers

# Define response serializers for different status codes


class BadRequestResponseSerializer(serializers.Serializer):
    """
    Serializer for a 400 Bad Request response.

    Attributes:
        message (CharField): A message describing the error. Defaults to "Bad request".
        data (DictField): Additional data about the error. Defaults to an empty dictionary.
    """

    message = serializers.CharField(default="Bad request")
    data = serializers.DictField(default={})


class UnauthorizedResponseSerializer(serializers.Serializer):
    """
    Serializer for a 401 Unauthorized response.

    Attributes:
        message (CharField): A message describing the error. Defaults to "Unauthorized".
    """

    message = serializers.CharField(default="Unauthorized")
    # data = serializers.DictField(default={})


class ForbiddenResponseSerializer(serializers.Serializer):
    """
    Serializer for a 403 Forbidden response.

    Attributes:
        message (CharField): A message describing the error. Defaults to "Not authenticated".
    """

    message = serializers.CharField(default="Not authenticated")
    # data = serializers.DictField(default={})


class NotFoundResponseSerializer(serializers.Serializer):
    """
    Serializer for a 404 Not Found response.

    Attributes:
        message (CharField): A message describing the error. Defaults to "Not Found".
    """

    message = serializers.CharField(default="Not Found")
    # data = serializers.DictField(default={})


class InternalServerErrorResponseSerializer(serializers.Serializer):
    """
    Serializer for a 500 Internal Server Error response.

    Attributes:
        message (CharField): A message describing the error. Defaults to "Internal Server Error".
    """

    message = serializers.CharField(default="Internal Server Error")
    # data = serializers.DictField(default={})


def get_response_schema():
    """
    Returns a dictionary of response schemas for various HTTP status codes.

    The dictionary maps HTTP status codes to `openapi.Response` objects,
    which describe the expected response for each status code.

    Returns:
        dict: A dictionary where keys are HTTP status codes (int) and values are `openapi.Response` objects.
    """
    return {
        400: openapi.Response(
            description="Bad request", schema=BadRequestResponseSerializer
        ),
        401: openapi.Response(
            description="Unauthorized", schema=UnauthorizedResponseSerializer
        ),
        403: openapi.Response(
            description="Not authenticated", schema=ForbiddenResponseSerializer
        ),
        404: openapi.Response(
            description="Not Found", schema=NotFoundResponseSerializer
        ),
        500: openapi.Response(
            description="Internal Server Error",
            schema=InternalServerErrorResponseSerializer,
        ),
        204: openapi.Response(description="No content"),
    }


def apply_swagger_tags(**kwargs):
    """
    A decorator to apply Swagger tags and additional metadata to API views.

    Args:

        **kwargs: Arbitrary keyword arguments.
            tags (list): List of tags to be applied to the Swagger documentation. Default is ["Test"].
            extra_actions (list): List of additional actions to apply the tags to. Default is an empty list.
            not_required_actions (list): List of actions that do not require detailed Swagger documentation. Default is ["update"].
            detailed_methods (list): List of methods to apply detailed Swagger documentation to. Default is ["create", "retrieve", "list", "partial_update", "destroy"].
            method_details (dict): Additional details to customize the documentation of specific methods.

    Returns:
        function: A decorator that applies the specified Swagger tags and metadata to the view methods.
    """
    tags = kwargs.get("tags", ["Test"])
    extra_actions = kwargs.get("extra_actions", [])
    not_required_actions = kwargs.get("not_required_actions", []) + ["update"]
    # detailed_methods = kwargs.get(
    #     "detailed_methods", ["create", "retrieve", "list", "partial_update", "destroy"]
    # )
    method_details = kwargs.get("method_details", {})

    def decorator(view):
        methods = {
            "create": {
                "operation_description": "Create API.",
                "operation_summary": "API to create new record.",
            },
            "retrieve": {
                "operation_description": "Retrieve API.",
                "operation_summary": "API for retrieve single record by id.",
            },
            "list": {
                "operation_description": "List API.",
                "operation_summary": "API to get list of records.",
            },
            "partial_update": {
                "operation_description": "Partial update API.",
                "operation_summary": "API for partial update record.",
            },
            "destroy": {
                "operation_description": "Delete API.",
                "operation_summary": "API to delete single record by id.",
            },
            "update": {
                "operation_description": "",
                "operation_summary": "",
            },
            "post": {
                "operation_description": "",
                "operation_summary": "",
                "request_body": None,
            },
            "get": {
                "operation_description": "",
                "operation_summary": "",
            },
        }

        for method, obj in method_details.items():
            if method in methods:
                methods[method].update(obj)

        for method, obj in methods.items():
            if hasattr(view, method):
                if method in extra_actions:
                    view_method = getattr(view, method)
                    setattr(
                        view,
                        method,
                        wraps(view_method)(
                            swagger_auto_schema(
                                tags=tags, responses=get_response_schema()
                            )(view_method)
                        ),
                    )
                elif method not in not_required_actions:
                    view_method = getattr(view, method)
                    setattr(
                        view,
                        method,
                        method_decorator(
                            name=method,
                            decorator=swagger_auto_schema(
                                tags=tags,
                                operation_summary=obj.get("operation_summary", ""),
                                operation_description=obj.get(
                                    "operation_description", ""
                                ),
                                request_body=obj.get("request_body", None),
                                responses=get_response_schema(),
                            ),
                        )(view_method),
                    )
                else:
                    view_method = getattr(view, method)
                    setattr(
                        view,
                        method,
                        method_decorator(
                            name=method,
                            decorator=swagger_auto_schema(tags=tags, auto_schema=None),
                        )(view_method),
                    )

        return view

    return decorator
