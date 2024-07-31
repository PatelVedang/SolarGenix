# from django.utils.decorators import method_decorator
# from drf_yasg.utils import swagger_auto_schema


# def apply_swagger_tags(**kwargs):
#     tags = kwargs.get("tags", "Test")
#     extra_actions = kwargs.get("extra_actions", [])
#     not_required_actions = kwargs.get("not_required_actions", []) + ["update"]
#     if extra_actions is None:
#         extra_actions = []

#     def decorator(viewset):
#         methods = {
#             "create": {
#                 "operation_description": "Create API.",
#                 "operation_summary": "API to create new record.",
#             },
#             "retrieve": {
#                 "operation_description": "Retrieve API.",
#                 "operation_summary": "API for retrieve single record by id.",
#             },
#             "list": {
#                 "operation_description": "List API.",
#                 "operation_summary": "API to get list of records.",
#             },
#             "partial_update": {
#                 "operation_description": "Partial update API.",
#                 "operation_summary": "API for partial update record.",
#             },
#             "destroy": {
#                 "operation_description": "Delete API.",
#                 "operation_summary": "API to delete single record by id.",
#             },
#             "update": {},
#             "post": {"operation_description": "", "operation_summary": ""},
#             "get": {"operation_description": "", "operation_summary": ""},
#         }
#         final_methods = {}

#         for method, obj in methods.items():
#             if hasattr(viewset, method):
#                 final_methods[method] = {*obj, *{"viewset": getattr(viewset, method)}}

#         for action in extra_actions:
#             setattr(
#                 viewset,
#                 action,
#                 swagger_auto_schema(tags=tags)(getattr(viewset, action)),
#             )

#         for action, obj in final_methods.items():
#             if not action in not_required_actions:
#                 setattr(
#                     viewset,
#                     action,
#                     method_decorator(
#                         name=action,
#                         decorator=swagger_auto_schema(
#                             tags=tags,
#                             operation_summary=obj["operation_summary"],
#                             operation_description=obj["operation_description"],
#                         ),
#                     )(obj["viewset"]),
#                 )
#             else:
#                 setattr(
#                     viewset,
#                     action,
#                     method_decorator(
#                         name=action,
#                         decorator=swagger_auto_schema(tags=tags, auto_schema=None),
#                     )(obj["viewset"]),
#                 )
#         return viewset

#     return decorator


from functools import wraps

# def apply_swagger_tags(tags=None, extra_actions=None, not_required_actions=None, detailed_methods=None):
#     if tags is None:
#         tags = ["Test"]
#     if extra_actions is None:
#         extra_actions = []
#     if not_required_actions is None:
#         not_required_actions = ["update"]
#     if detailed_methods is None:
#         detailed_methods = ["create", "retrieve", "list", "partial_update", "destroy"]
#     def decorator(viewset):
#         methods = {
#             "create": {
#                 "operation_description": "Create API.",
#                 "operation_summary": "API to create new record.",
#             },
#             "retrieve": {
#                 "operation_description": "Retrieve API.",
#                 "operation_summary": "API for retrieve single record by id.",
#             },
#             "list": {
#                 "operation_description": "List API.",
#                 "operation_summary": "API to get list of records.",
#             },
#             "partial_update": {
#                 "operation_description": "Partial update API.",
#                 "operation_summary": "API for partial update record.",
#             },
#             "destroy": {
#                 "operation_description": "Delete API.",
#                 "operation_summary": "API to delete single record by id.",
#             },
#             "update": {
#                 "operation_description": "",
#                 "operation_summary": "",
#             },
#             "post": {
#                 "operation_description": "",
#                 "operation_summary": "",
#             },
#             "get": {
#                 "operation_description": "",
#                 "operation_summary": "",
#             },
#         }
#         final_methods = {}
#         for method, obj in methods.items():
#             if hasattr(viewset, method):
#                 final_methods[method] = {**obj, "viewset": getattr(viewset, method)}
#         for action in extra_actions:
#             setattr(
#                 viewset,
#                 action,
#                 swagger_auto_schema(tags=tags)(getattr(viewset, action)),
#             )
#         for action, obj in final_methods.items():
#             if action in detailed_methods:
#                 setattr(
#                     viewset,
#                     action,
#                     method_decorator(
#                         name=action,
#                         decorator=swagger_auto_schema(
#                             tags=tags,
#                             operation_summary=obj["operation_summary"],
#                             operation_description=obj["operation_description"],
#                         ),
#                     )(obj["viewset"]),
#                 )
#             else:
#                 setattr(
#                     viewset,
#                     action,
#                     method_decorator(
#                         name=action,
#                         decorator=swagger_auto_schema(tags=tags),
#                     )(obj["viewset"]),
#                 )
#         return viewset
#     return decorator
# def apply_swagger_tags(tags=None, extra_actions=None, not_required_actions=None, detailed_methods=None, method_details=None):
#     if tags is None:
#         tags = ["Test"]
#     if extra_actions is None:
#         extra_actions = []
#     if not_required_actions is None:
#         not_required_actions = ["update"]
#     if detailed_methods is None:
#         detailed_methods = ["create", "retrieve", "list", "partial_update", "destroy"]
#     if method_details is None:
#         method_details = {}
#     def decorator(view):
#         methods = {
#             "create": {
#                 "operation_description": "Create API.",
#                 "operation_summary": "API to create new record.",
#             },
#             "retrieve": {
#                 "operation_description": "Retrieve API.",
#                 "operation_summary": "API for retrieve single record by id.",
#             },
#             "list": {
#                 "operation_description": "List API.",
#                 "operation_summary": "API to get list of records.",
#             },
#             "partial_update": {
#                 "operation_description": "Partial update API.",
#                 "operation_summary": "API for partial update record.",
#             },
#             "destroy": {
#                 "operation_description": "Delete API.",
#                 "operation_summary": "API to delete single record by id.",
#             },
#             "update": {
#                 "operation_description": "",
#                 "operation_summary": "",
#             },
#             "post": {
#                 "operation_description": "",
#                 "operation_summary": "",
#                 "request_body": None,
#             },
#             "get": {
#                 "operation_description": "",
#                 "operation_summary": "",
#             },
#         }
#         for method, obj in method_details.items():
#             if method in methods:
#                 methods[method].update(obj)
#         for action, obj in methods.items():
#             if hasattr(view, action):
#                 decorator = swagger_auto_schema(
#                     tags=tags,
#                     operation_summary=obj.get("operation_summary", ""),
#                     operation_description=obj.get("operation_description", ""),
#                     request_body=obj.get("request_body", None),
#                 )
#                 method_decorator(name=action, decorator=decorator)(view)
#         return view
#     return decorator
# def apply_swagger_tags(tags=None, extra_actions=None, not_required_actions=None, detailed_methods=None, method_details=None):
#     if tags is None:
#         tags = ["Test"]
#     if extra_actions is None:
#         extra_actions = []
#     if not_required_actions is None:
#         not_required_actions = ["update"]
#     if detailed_methods is None:
#         detailed_methods = ["create", "retrieve", "list", "partial_update", "destroy"]
#     if method_details is None:
#         method_details = {}
#     common_responses = {
#         401: 'Unauthorized',
#         204: 'No Content',
#         404: 'Not Found',
#     }
#     def decorator(view):
#         methods = {
#             "create": {
#                 "operation_description": "Create API.",
#                 "operation_summary": "API to create new record.",
#                 "responses": common_responses,
#             },
#             "retrieve": {
#                 "operation_description": "Retrieve API.",
#                 "operation_summary": "API to retrieve single record by id.",
#                 "responses": common_responses,
#             },
#             "list": {
#                 "operation_description": "List API.",
#                 "operation_summary": "API to get list of records.",
#                 "responses": common_responses,
#             },
#             "partial_update": {
#                 "operation_description": "Partial update API.",
#                 "operation_summary": "API for partial update record.",
#                 "responses": common_responses,
#             },
#             "destroy": {
#                 "operation_description": "Delete API.",
#                 "operation_summary": "API to delete single record by id.",
#                 "responses": common_responses,
#             },
#             "update": {
#                 "operation_description": "",
#                 "operation_summary": "",
#                 "responses": common_responses,
#             },
#             "post": {
#                 "operation_description": "",
#                 "operation_summary": "",
#                 "request_body": None,
#                 "responses": common_responses,
#             },
#             "get": {
#                 "operation_description": "",
#                 "operation_summary": "",
#                 "responses": common_responses,
#             },
#         }
#         for method, obj in method_details.items():
#             if method in methods:
#                 methods[method].update(obj)
#         for action, obj in methods.items():
#             if hasattr(view, action):
#                 decorator = swagger_auto_schema(
#                     tags=tags,
#                     operation_summary=obj.get("operation_summary", ""),
#                     operation_description=obj.get("operation_description", ""),
#                     request_body=obj.get("request_body", None),
#                     responses=obj.get("responses", common_responses),
#                 )
#                 method_decorator(name=action, decorator=decorator)(view)
#         return view
#     return decorator
# class GenericResponseSerializer(serializers.Serializer):
#     message = serializers.CharField()
#     data = serializers.DictField(required=False, allow_null=True)
# # Define a function to get response schemas
# def get_response_schema():
#     return {
#         400: GenericResponseSerializer,
#         401: GenericResponseSerializer,
#         403: GenericResponseSerializer,
#         404: GenericResponseSerializer,
#         500: GenericResponseSerializer,
#         204: None  # For no content responses
#     }
# # Define the decorator to apply Swagger tags and schemas
# def apply_swagger_tags(tags=None, extra_actions=None, not_required_actions=None, detailed_methods=None, method_details=None):
#     if tags is None:
#         tags = ["Test"]
#     if extra_actions is None:
#         extra_actions = []
#     if not_required_actions is None:
#         not_required_actions = ["update"]
#     if detailed_methods is None:
#         detailed_methods = ["create", "retrieve", "list", "partial_update", "destroy"]
#     if method_details is None:
#         method_details = {}
#     def decorator(view):
#         methods = {
#             "create": {
#                 "operation_description": "Create API.",
#                 "operation_summary": "API to create new record.",
#             },
#             "retrieve": {
#                 "operation_description": "Retrieve API.",
#                 "operation_summary": "API for retrieve single record by id.",
#             },
#             "list": {
#                 "operation_description": "List API.",
#                 "operation_summary": "API to get list of records.",
#             },
#             "partial_update": {
#                 "operation_description": "Partial update API.",
#                 "operation_summary": "API for partial update record.",
#             },
#             "destroy": {
#                 "operation_description": "Delete API.",
#                 "operation_summary": "API to delete single record by id.",
#             },
#             "update": {
#                 "operation_description": "",
#                 "operation_summary": "",
#             },
#             "post": {
#                 "operation_description": "",
#                 "operation_summary": "",
#                 "request_body": None,
#             },
#             "get": {
#                 "operation_description": "",
#                 "operation_summary": "",
#             },
#         }
#         for method, obj in method_details.items():
#             if method in methods:
#                 methods[method].update(obj)
#         for action, obj in methods.items():
#             if hasattr(view, action):
#                 schema_decorator = swagger_auto_schema(
#                     tags=tags,
#                     operation_summary=obj.get("operation_summary", ""),
#                     operation_description=obj.get("operation_description", ""),
#                     request_body=obj.get("request_body", None),
#                     responses=get_response_schema()
#                 )
#                 view_method = getattr(view, action)
#                 setattr(view, action, wraps(view_method)(schema_decorator(view_method)))
#         return view
#     return decorator
# # Define response serializers for different status codes
# class BadRequestResponseSerializer(serializers.Serializer):
#     message = serializers.CharField(default="Bad request")
#     data = serializers.DictField(default={})
# class UnauthorizedResponseSerializer(serializers.Serializer):
#     message = serializers.CharField(default="Unauthorized")
#     data = serializers.DictField(default={})
# class ForbiddenResponseSerializer(serializers.Serializer):
#     message = serializers.CharField(default="Not authenticated")
#     data = serializers.DictField(default={})
# class NotFoundResponseSerializer(serializers.Serializer):
#     message = serializers.CharField(default="Not Found")
#     data = serializers.DictField(default={})
# class InternalServerErrorResponseSerializer(serializers.Serializer):
#     message = serializers.CharField(default="Internal Server Error")
#     data = serializers.DictField(default={})
# class DefaultSchema:
#     def __init__(self):
#         self.defaults = {
#             400: BadRequestResponseSerializer,
#             401: UnauthorizedResponseSerializer,
#             403: ForbiddenResponseSerializer,
#             404: NotFoundResponseSerializer,
#             500: InternalServerErrorResponseSerializer,
#             204: None  # For no content responses
#         }
#     def response_schema(self):
#         return self.defaults
# default_schema = DefaultSchema()
# # Define the decorator to apply Swagger tags and schemas
# def apply_swagger_tags(tags=None, method_details=None):
#     if tags is None:
#         tags = ["Default"]
#     if method_details is None:
#         method_details = {}
#     def decorator(view):
#         methods = {
#             "create": {
#                 "operation_description": "Create API.",
#                 "operation_summary": "API to create new record.",
#             },
#             "retrieve": {
#                 "operation_description": "Retrieve API.",
#                 "operation_summary": "API for retrieve single record by id.",
#             },
#             "list": {
#                 "operation_description": "List API.",
#                 "operation_summary": "API to get list of records.",
#             },
#             "partial_update": {
#                 "operation_description": "Partial update API.",
#                 "operation_summary": "API for partial update record.",
#             },
#             "destroy": {
#                 "operation_description": "Delete API.",
#                 "operation_summary": "API to delete single record by id.",
#             },
#             "update": {
#                 "operation_description": "",
#                 "operation_summary": "",
#             },
#             "post": {
#                 "operation_description": "",
#                 "operation_summary": "",
#                 "request_body": None,
#             },
#             "get": {
#                 "operation_description": "",
#                 "operation_summary": "",
#             },
#         }
#         for method, obj in method_details.items():
#             if method in methods:
#                 methods[method].update(obj)
#         for action, obj in methods.items():
#             if hasattr(view, action):
#                 responses = default_schema.response_schema()  # Get default responses
#                 # Filter out any None entries
#                 responses = {code: {"serializer": serializer} for code, serializer in responses.items() if serializer is not None}
#                 schema_decorator = swagger_auto_schema(
#                     tags=tags,
#                     operation_summary=obj.get("operation_summary", ""),
#                     operation_description=obj.get("operation_description", ""),
#                     request_body=obj.get("request_body", None),
#                     responses=responses
#                 )
#                 view_method = getattr(view, action)
#                 setattr(view, action, wraps(view_method)(schema_decorator(view_method)))
#         return view
#     return decorator
#
# Define response serializers for different status codes
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers

# class BadRequestResponseSerializer(serializers.Serializer):
#     message = serializers.CharField(default="Bad request")
#     data = serializers.DictField(default={})

# class UnauthorizedResponseSerializer(serializers.Serializer):
#     message = serializers.CharField(default="Unauthorized")
#     data = serializers.DictField(default={})

# class ForbiddenResponseSerializer(serializers.Serializer):
#     message = serializers.CharField(default="Not authenticated")
#     data = serializers.DictField(default={})

# class NotFoundResponseSerializer(serializers.Serializer):
#     message = serializers.CharField(default="Not Found")
#     data = serializers.DictField(default={})

# class InternalServerErrorResponseSerializer(serializers.Serializer):
#     message = serializers.CharField(default="Internal Server Error")
#     data = serializers.DictField(default={})

# # Define a function to get response schemas
# def get_response_schema():
#     return {
#         400: openapi.Response(
#             description="Bad request",
#             schema=BadRequestResponseSerializer
#         ),
#         401: openapi.Response(
#             description="Unauthorized",
#             schema=UnauthorizedResponseSerializer
#         ),
#         403: openapi.Response(
#             description="Not authenticated",
#             schema=ForbiddenResponseSerializer
#         ),
#         404: openapi.Response(
#             description="Not Found",
#             schema=NotFoundResponseSerializer
#         ),
#         500: openapi.Response(
#             description="Internal Server Error",
#             schema=InternalServerErrorResponseSerializer
#         ),
#         204: openapi.Response(description="No content")
#     }

# # Define the decorator to apply Swagger tags and schemas
# def apply_swagger_tags(tags=None, extra_actions=None, not_required_actions=None, detailed_methods=None, method_details=None):
#     if tags is None:
#         tags = ["Test"]
#     if extra_actions is None:
#         extra_actions = []
#     if not_required_actions is None:
#         not_required_actions = ["update"]
#     if detailed_methods is None:
#         detailed_methods = ["create", "retrieve", "list", "partial_update", "destroy"]
#     if method_details is None:
#         method_details = {}

#     def decorator(view):
#         methods = {
#             "create": {
#                 "operation_description": "Create API.",
#                 "operation_summary": "API to create new record.",
#             },
#             "retrieve": {
#                 "operation_description": "Retrieve API.",
#                 "operation_summary": "API for retrieve single record by id.",
#             },
#             "list": {
#                 "operation_description": "List API.",
#                 "operation_summary": "API to get list of records.",
#             },
#             "partial_update": {
#                 "operation_description": "Partial update API.",
#                 "operation_summary": "API for partial update record.",
#             },
#             "destroy": {
#                 "operation_description": "Delete API.",
#                 "operation_summary": "API to delete single record by id.",
#             },
#             "update": {
#                 "operation_description": "",
#                 "operation_summary": "",
#             },
#             "post": {
#                 "operation_description": "",
#                 "operation_summary": "",
#                 "request_body": None,
#             },
#             "get": {
#                 "operation_description": "",
#                 "operation_summary": "",
#             },
#         }

#         for method, obj in method_details.items():
#             if method in methods:
#                 methods[method].update(obj)

#         for action, obj in methods.items():
#             if hasattr(view, action):
#                 schema_decorator = swagger_auto_schema(
#                     tags=tags,
#                     operation_summary=obj.get("operation_summary", ""),
#                     operation_description=obj.get("operation_description", ""),
#                     request_body=obj.get("request_body", None),
#                     responses=get_response_schema()
#                 )
#                 view_method = getattr(view, action)
#                 setattr(view, action, wraps(view_method)(schema_decorator(view_method)))

#         return view


#     return decorator
class BadRequestResponseSerializer(serializers.Serializer):
    message = serializers.CharField(default="Bad request")
    data = serializers.DictField(default={})


class UnauthorizedResponseSerializer(serializers.Serializer):
    message = serializers.CharField(default="Unauthorized")
    # data = serializers.DictField(default={})


class ForbiddenResponseSerializer(serializers.Serializer):
    message = serializers.CharField(default="Not authenticated")
    # data = serializers.DictField(default={})


class NotFoundResponseSerializer(serializers.Serializer):
    message = serializers.CharField(default="Not Found")
    # data = serializers.DictField(default={})


class InternalServerErrorResponseSerializer(serializers.Serializer):
    message = serializers.CharField(default="Internal Server Error")
    # data = serializers.DictField(default={})


class TooManyRequestsErrorResponseSerializer(serializers.Serializer):
    message = serializers.CharField(default="Too Many Requests")


def get_response_schema():
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
            description="Not Found", schema=TooManyRequestsErrorResponseSerializer
        ),
        500: openapi.Response(
            description="Internal Server Error",
            schema=InternalServerErrorResponseSerializer,
        ),
        204: openapi.Response(description="No content"),
    }


def apply_swagger_tags(
    tags=None,
    extra_actions=None,
    not_required_actions=None,
    detailed_methods=None,
    method_details=None,
):
    if tags is None:
        tags = ["Test"]
    if extra_actions is None:
        extra_actions = []
    if not_required_actions is None:
        not_required_actions = ["update"]
    if detailed_methods is None:
        detailed_methods = ["create", "retrieve", "list", "partial_update", "destroy"]
    if method_details is None:
        method_details = {}

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

        for action, obj in methods.items():
            if hasattr(view, action):
                schema_decorator = swagger_auto_schema(
                    tags=tags,
                    operation_summary=obj.get("operation_summary", ""),
                    operation_description=obj.get("operation_description", ""),
                    request_body=obj.get("request_body", None),
                    responses=get_response_schema(),
                )
                view_method = getattr(view, action)
                setattr(view, action, wraps(view_method)(schema_decorator(view_method)))

        return view

    return decorator
