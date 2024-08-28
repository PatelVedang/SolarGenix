from functools import wraps
from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers


# Define response serializers for different status codes
class BadRequestResponseSerializer(serializers.Serializer):
    message = serializers.CharField(default="Bad request")
    data = serializers.DictField(default={})


class UnauthorizedResponseSerializer(serializers.Serializer):
    message = serializers.CharField(default="Unauthorized")


class ForbiddenResponseSerializer(serializers.Serializer):
    message = serializers.CharField(default="Not authenticated")


class NotFoundResponseSerializer(serializers.Serializer):
    message = serializers.CharField(default="Not Found")


class InternalServerErrorResponseSerializer(serializers.Serializer):
    message = serializers.CharField(default="Internal Server Error")


class TooManyRequestsErrorResponseSerializer(serializers.Serializer):
    message = serializers.CharField(default="Too Many Requests")


def get_response_schema():
    """
    Returns a dictionary of response schemas for various HTTP status codes.
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
        429: openapi.Response(
            description="Too Many Requests",
            schema=TooManyRequestsErrorResponseSerializer,
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
    tags = kwargs.get("tags", ["Default"])
    extra_actions = kwargs.get("extra_actions", [])
    not_required_actions = kwargs.get("not_required_actions", ["update"])
    method_details = kwargs.get("method_details", {})

    def decorator(view):
        # Default method metadata
        methods = {
            "create": {
                "operation_description": "Create a new record.",
                "operation_summary": "Create API",
            },
            "retrieve": {
                "operation_description": "Retrieve a record by ID.",
                "operation_summary": "Retrieve API",
            },
            "list": {
                "operation_description": "Get a list of records.",
                "operation_summary": "List API",
            },
            "partial_update": {
                "operation_description": "Partially update a record.",
                "operation_summary": "Partial Update API",
            },
            "destroy": {
                "operation_description": "Delete a record by ID.",
                "operation_summary": "Delete API",
            },
            "update": {
                "operation_description": "Update a record by ID.",
                "operation_summary": "Update API",
            },
            "post": {
                "operation_description": "Submit data.",
                "operation_summary": "Post API",
                "request_body": None,
            },
            "get": {
                "operation_description": "Fetch data.",
                "operation_summary": "Get API",
            },
        }

        # Customize method metadata if provided
        for method, obj in method_details.items():
            if method in methods:
                methods[method].update(obj)
            else:
                methods[method] = obj

        # Apply decorators
        for method, obj in methods.items():
            if hasattr(view, method):
                view_method = getattr(view, method)
                if method in extra_actions:
                    setattr(
                        view,
                        method,
                        wraps(view_method)(
                            swagger_auto_schema(
                                tags=tags,
                                operation_description=obj.get(
                                    "operation_description", ""
                                ),
                                operation_summary=obj.get("operation_summary", ""),
                                responses=get_response_schema(),
                            )(view_method)
                        ),
                    )
                elif method not in not_required_actions:
                    if hasattr(view_method, "_swagger_auto_schema"):
                        # Add tags and other details to existing Swagger decorators
                        if "_swagger_auto_schema" in dir(view_method):
                            decorator_data = getattr(
                                view_method, "_swagger_auto_schema"
                            )
                            decorator_data.update(tags=tags, **obj)
                    else:
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
                    if hasattr(view_method, "_swagger_auto_schema"):
                        # Add tags to existing Swagger decorators
                        if "_swagger_auto_schema" in dir(view_method):
                            decorator_data = getattr(
                                view_method, "_swagger_auto_schema"
                            )
                            decorator_data.update(tags=tags, auto_schema=None)
                    else:
                        setattr(
                            view,
                            method,
                            method_decorator(
                                name=method,
                                decorator=swagger_auto_schema(
                                    tags=tags, auto_schema=None
                                ),
                            )(view_method),
                        )

        return view

    return decorator
