# from drf_yasg import openapi
# from functools import wraps
# from django.conf import settings
# from django.http import HttpResponse
# from drf_yasg.utils import swagger_auto_schema
# from drf_yasg.generators import OpenAPISchemaGenerator
# from django.utils.decorators import method_decorator
# from rest_framework import serializers
#

# # Define response serializers for different status codes
# class BadRequestResponseSerializer(serializers.Serializer):
#     message = serializers.CharField(default="Bad request")
#     data = serializers.DictField(default={})


# class UnauthorizedResponseSerializer(serializers.Serializer):
#     message = serializers.CharField(default="Unauthorized")


# class ForbiddenResponseSerializer(serializers.Serializer):
#     message = serializers.CharField(default="Not authenticated")


# class NotFoundResponseSerializer(serializers.Serializer):
#     message = serializers.CharField(default="Not Found")


# class InternalServerErrorResponseSerializer(serializers.Serializer):
#     message = serializers.CharField(default="Internal Server Error")


# class TooManyRequestsErrorResponseSerializer(serializers.Serializer):
#     message = serializers.CharField(default="Too Many Requests")


# def get_response_schema():
#     """
#     Returns a dictionary of response schemas for various HTTP status codes.
#     """
#     return {
#         400: openapi.Response(
#             description="Bad request", schema=BadRequestResponseSerializer
#         ),
#         401: openapi.Response(
#             description="Unauthorized", schema=UnauthorizedResponseSerializer
#         ),
#         403: openapi.Response(
#             description="Not authenticated", schema=ForbiddenResponseSerializer
#         ),
#         404: openapi.Response(
#             description="Not Found", schema=NotFoundResponseSerializer
#         ),
#         429: openapi.Response(
#             description="Too Many Requests",
#             schema=TooManyRequestsErrorResponseSerializer,
#         ),
#         500: openapi.Response(
#             description="Internal Server Error",
#             schema=InternalServerErrorResponseSerializer,
#         ),
#         204: openapi.Response(description="No content"),
#     }


# def set_attr(view, method, tags, obj, view_method, extra_action):
#     params = {
#         "operation_description": obj.get("operation_description", ""),
#         "operation_summary": obj.get("operation_summary", ""),
#         "responses": get_response_schema(),
#         "tags": tags,
#     }
#     if method == "list":
#         params["manual_parameters"] = [
#             openapi.Parameter(
#                 "fields",
#                 openapi.IN_QUERY,
#                 description="Comma separated fields",
#                 type=openapi.TYPE_STRING,
#             ),
#             openapi.Parameter(
#                 name="sort",
#                 in_=openapi.IN_QUERY,
#                 description="Fields to sort",
#                 type=openapi.TYPE_STRING,
#             ),
#             openapi.Parameter(
#                 name="search",
#                 in_=openapi.IN_QUERY,
#                 description="Search term.",
#                 type=openapi.TYPE_STRING,
#             ),
#             openapi.Parameter(
#                 name="search_fields",
#                 in_=openapi.IN_QUERY,
#                 description="Fields on search ",
#                 type=openapi.TYPE_STRING,
#             ),
#         ]
#     elif method == "retrieve":
#         params["manual_parameters"] = [
#             openapi.Parameter(
#                 "fields",
#                 openapi.IN_QUERY,
#                 description="Comma separated fields",
#                 type=openapi.TYPE_STRING,
#             )
#         ]

#     if extra_action:
#         setattr(
#             view,
#             method,
#             wraps(view_method)(
#                 swagger_auto_schema(
#                     tags=tags,
#                     operation_description=obj.get("operation_description", ""),
#                     operation_summary=obj.get("operation_summary", ""),
#                     responses=get_response_schema(),
#                 )(view_method)
#             ),
#         )
#     else:
#         setattr(
#             view,
#             method,
#             method_decorator(name=method, decorator=swagger_auto_schema(**params))(
#                 view_method
#             ),
#         )


# def apply_swagger_tags(**kwargs):
#     """
#     A decorator to apply Swagger tags and additional metadata to API views.

#     Args:

#         **kwargs: Arbitrary keyword arguments.
#             tags (list): List of tags to be applied to the Swagger documentation. Default is ["Test"].
#             extra_actions (list): List of additional actions to apply the tags to. Default is an empty list.
#             not_required_actions (list): List of actions that do not require detailed Swagger documentation. Default is ["update"].
#             detailed_methods (list): List of methods to apply detailed Swagger documentation to. Default is ["create", "retrieve", "list", "partial_update", "destroy"].
#             method_details (dict): Additional details to customize the documentation of specific methods.

#     Returns:
#         function: A decorator that applies the specified Swagger tags and metadata to the view methods.
#     """
#     tags = kwargs.get("tags", ["Default"])
#     extra_actions = kwargs.get("extra_actions", [])
#     not_required_actions = kwargs.get("not_required_actions", ["update"])
#     method_details = kwargs.get("method_details", {})

#     def decorator(view):
#         # Default method metadata
#         methods = {
#             "create": {
#                 "operation_description": "Create a new record.",
#                 "operation_summary": "Create API",
#             },
#             "retrieve": {
#                 "operation_description": "Retrieve a record by ID.",
#                 "operation_summary": "Retrieve API",
#             },
#             "list": {
#                 "operation_description": "Get a list of records.",
#                 "operation_summary": "List API",
#             },
#             "partial_update": {
#                 "operation_description": "Partially update a record.",
#                 "operation_summary": "Partial Update API",
#             },
#             "destroy": {
#                 "operation_description": "Delete a record by ID.",
#                 "operation_summary": "Delete API",
#             },
#             "update": {
#                 "operation_description": "Update a record by ID.",
#                 "operation_summary": "Update API",
#             },
#             "post": {
#                 "operation_description": "Submit data.",
#                 "operation_summary": "Post API",
#                 "request_body": None,
#             },
#             "get": {
#                 "operation_description": "Fetch data.",
#                 "operation_summary": "Get API",
#             },
#         }

#         # Customize method metadata if provided
#         for method, obj in method_details.items():
#             if method in methods:
#                 methods[method].update(obj)
#             else:
#                 methods[method] = obj

#         # Apply decorators
#         for method, obj in methods.items():
#             if hasattr(view, method):
#                 view_method = getattr(view, method)
#                 if method in extra_actions:
#                     set_attr(view, method, tags, obj, view_method, True)
#                 elif method not in not_required_actions:
#                     if hasattr(view_method, "_swagger_auto_schema"):
#                         # Add tags and other details to existing Swagger decorators
#                         if "_swagger_auto_schema" in dir(view_method):
#                             decorator_data = getattr(
#                                 view_method, "_swagger_auto_schema"
#                             )
#                             decorator_data.update(tags=tags, **obj)
#                     else:
#                         set_attr(view, method, tags, obj, view_method, False)
#                 else:
#                     if hasattr(view_method, "_swagger_auto_schema"):
#                         if "_swagger_auto_schema" in dir(view_method):
#                             decorator_data = getattr(
#                                 view_method, "_swagger_auto_schema"
#                             )
#                             decorator_data.update(tags=tags, auto_schema=None)
#                     else:
#                         set_attr(view, method, tags, obj, view_method, False)

#         return view

#     return decorator


# def swagger_auth_required(view_func):
#     """
#     Custom decorator to force Basic Auth for Swagger UI.
#     """

#     def _wrapped_view(request, *args, **kwargs):
#         # Get username and password from .env (you can use django-environ for this)
#         from base64 import b64decode

#         AUTH_USER = settings.SWAGGER_AUTH_USERNAME
#         AUTH_PASS = settings.SWAGGER_AUTH_PASSWORD

#         # Extract credentials from request headers
#         auth_header = request.META.get("HTTP_AUTHORIZATION")
#         if auth_header and auth_header.startswith("Basic "):
#             credentials = b64decode(auth_header.split(" ")[1]).decode("utf-8")
#             email, password = credentials.split(":", 1)
#             # Check credentials
#             if email == AUTH_USER and password == AUTH_PASS:
#                 return view_func(request, *args, **kwargs)

#         # Return Unauthorized if credentials are incorrect
#         response = HttpResponse("Unauthorized", status=401)
#         response["WWW-Authenticate"] = 'Basic realm="Swagger"'
#         return response

#     return _wrapped_view


# class HttpAndHttpsSchemaGenerator(OpenAPISchemaGenerator):
#     def get_schema(self, request=None, public=False):
#         schema = super().get_schema(request, public)
#         schema.schemes = ["http", "https"]
#         return schema


from base64 import b64decode
from functools import wraps

from django.conf import settings
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import serializers


# Define response serializers for different status codes
class SuccessResponseSerializer(serializers.Serializer):
    message = serializers.CharField(default="Request was successful")
    data = serializers.DictField(default={})


class BadRequestResponseSerializer(serializers.Serializer):
    message = serializers.CharField(default="Bad request")
    data = serializers.DictField(default={})


class UnauthorizedResponseSerializer(serializers.Serializer):
    message = serializers.CharField(default="Unauthorized")
    data = serializers.DictField(default={})


class ForbiddenResponseSerializer(serializers.Serializer):
    message = serializers.CharField(default="Not authenticated")
    data = serializers.DictField(default={})


class NotFoundResponseSerializer(serializers.Serializer):
    message = serializers.CharField(default="Not Found")
    data = serializers.DictField(default={})


class InternalServerErrorResponseSerializer(serializers.Serializer):
    message = serializers.CharField(default="Internal Server Error")
    data = serializers.DictField(default={})


class TooManyRequestsErrorResponseSerializer(serializers.Serializer):
    message = serializers.CharField(default="Too Many Requests")
    data = serializers.DictField(default={})


class UnprocessableEntityResponseSerializer(serializers.Serializer):
    message = serializers.CharField(default="Validation errors")
    data = serializers.DictField(default={})


def get_response_schema():
    """
    Returns a dictionary of response schemas for various HTTP status codes.
    """
    return {
        200: OpenApiResponse(
            response=SuccessResponseSerializer, description="Request was successful"
        ),
        400: OpenApiResponse(
            response=BadRequestResponseSerializer, description="Bad request"
        ),
        401: OpenApiResponse(
            response=UnauthorizedResponseSerializer, description="Unauthorized"
        ),
        403: OpenApiResponse(
            response=ForbiddenResponseSerializer, description="Not authenticated"
        ),
        404: OpenApiResponse(
            response=NotFoundResponseSerializer, description="Not Found"
        ),
        429: OpenApiResponse(
            response=TooManyRequestsErrorResponseSerializer,
            description="Too Many Requests",
        ),
        422: OpenApiResponse(
            response=UnprocessableEntityResponseSerializer,
            description="Unprocessable Entity",
        ),
        500: OpenApiResponse(
            response=InternalServerErrorResponseSerializer,
            description="Internal Server Error",
        ),
        204: OpenApiResponse(description="No content"),
    }


def set_attr(view, method, tags, obj, view_method, extra_action):
    params = {
        "description": obj.get("description", ""),
        "summary": obj.get("summary", ""),
        "responses": get_response_schema(),
        "tags": tags,
    }

    if method == "list":
        params["parameters"] = [
            OpenApiParameter(
                name="fields",
                location=OpenApiParameter.QUERY,
                description="Comma separated fields",
                type=str,
            ),
            OpenApiParameter(
                name="sort",
                location=OpenApiParameter.QUERY,
                description="Fields to sort",
                type=str,
            ),
            OpenApiParameter(
                name="search",
                location=OpenApiParameter.QUERY,
                description="Search term.",
                type=str,
            ),
            OpenApiParameter(
                name="search_fields",
                location=OpenApiParameter.QUERY,
                description="Fields on search",
                type=str,
            ),
        ]
    elif method == "retrieve":
        params["parameters"] = [
            OpenApiParameter(
                name="fields",
                location=OpenApiParameter.QUERY,
                description="Comma separated fields",
                type=str,
            )
        ]

    if extra_action:
        setattr(
            view,
            method,
            wraps(view_method)(
                extend_schema(
                    tags=tags,
                    description=obj.get("description", ""),
                    summary=obj.get("summary", ""),
                    responses=get_response_schema(),
                )(view_method)
            ),
        )
    else:
        setattr(
            view,
            method,
            method_decorator(name=method, decorator=extend_schema(**params))(
                view_method
            ),
        )


def apply_swagger_tags(**kwargs):
    """
    A decorator to apply Swagger tags and additional metadata to API views.

    Args:
        **kwargs: Arbitrary keyword arguments.
            tags (list): List of tags to be applied to the Swagger documentation. Default is ["Default"].
            extra_actions (list): List of additional actions to apply the tags to. Default is an empty list.
            not_required_actions (list): List of actions that do not require detailed Swagger documentation. Default is ["update"].
            detailed_methods (list): List of methods to apply detailed Swagger documentation to. Default is ["create", "retrieve", "list", "partial_update", "destroy"].
            method_details (dict): Additional details to customize the documentation of specific methods.
    """
    tags = kwargs.get("tags", ["Default"])
    extra_actions = kwargs.get("extra_actions", [])
    not_required_actions = kwargs.get("not_required_actions", ["update"])
    method_details = kwargs.get("method_details", {})

    def decorator(view):
        # Default method metadata
        methods = {
            "create": {
                "description": "Create a new record.",
                "summary": "Create API",
            },
            "retrieve": {
                "description": "Retrieve a record by ID.",
                "summary": "Retrieve API",
            },
            "list": {
                "description": "Get a list of records.",
                "summary": "List API",
            },
            "partial_update": {
                "description": "Partially update a record.",
                "summary": "Partial Update API",
            },
            "destroy": {
                "description": "Delete a record by ID.",
                "summary": "Delete API",
            },
            "update": {
                "description": "Update a record by ID.",
                "summary": "Update API",
            },
            "post": {
                "description": "Submit data.",
                "summary": "Post API",
                "request_body": None,
            },
            "get": {
                "description": "Fetch data.",
                "summary": "Get API",
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
                    set_attr(view, method, tags, obj, view_method, True)
                elif method not in not_required_actions:
                    if hasattr(view_method, "_extend_schema"):
                        if "_extend_schema" in dir(view_method):
                            decorator_data = getattr(view_method, "_extend_schema")
                            decorator_data.update(tags=tags, **obj)
                    else:
                        set_attr(view, method, tags, obj, view_method, False)
                else:
                    if hasattr(view_method, "_extend_schema"):
                        if "_extend_schema" in dir(view_method):
                            decorator_data = getattr(view_method, "_extend_schema")
                            decorator_data.update(tags=tags, auto_schema=None)
                    else:
                        set_attr(view, method, tags, obj, view_method, False)

        return view

    return decorator


def swagger_auth_required(view_func):
    """
    Custom decorator to force Basic Auth for Swagger UI access.
    """

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Static credentials stored in settings.py
        AUTH_USER = settings.SWAGGER_AUTH_USERNAME
        AUTH_PASS = settings.SWAGGER_AUTH_PASSWORD

        # Get the Authorization header
        auth_header = request.META.get("HTTP_AUTHORIZATION")
        if auth_header and auth_header.startswith("Basic "):
            # Decode base64 and check credentials
            credentials = b64decode(auth_header.split(" ")[1]).decode("utf-8")
            username, password = credentials.split(":", 1)
            if username == AUTH_USER and password == AUTH_PASS:
                return view_func(request, *args, **kwargs)

        # Return 401 Unauthorized if the credentials don't match
        response = HttpResponse("Unauthorized", status=401)
        response["WWW-Authenticate"] = 'Basic realm="Swagger"'
        return response

    return _wrapped_view
