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

from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema

def apply_swagger_tags(tags=None, extra_actions=None, not_required_actions=None, detailed_methods=None):
    if tags is None:
        tags = ["Test"]
    if extra_actions is None:
        extra_actions = []
    if not_required_actions is None:
        not_required_actions = ["update"]
    if detailed_methods is None:
        detailed_methods = ["create", "retrieve", "list", "partial_update", "destroy"]

    def decorator(viewset):
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
            },
            "get": {
                "operation_description": "",
                "operation_summary": "",
            },
        }
        final_methods = {}

        for method, obj in methods.items():
            if hasattr(viewset, method):
                final_methods[method] = {*obj, *{"viewset": getattr(viewset, method)}}

        for action in extra_actions:
            setattr(
                viewset,
                action,
                swagger_auto_schema(tags=tags)(getattr(viewset, action)),
            )

        for action, obj in final_methods.items():
            if action in detailed_methods:
                setattr(
                    viewset,
                    action,
                    method_decorator(
                        name=action,
                        decorator=swagger_auto_schema(
                            tags=tags,
                            operation_summary=obj["operation_summary"],
                            operation_description=obj["operation_description"],
                        ),
                    )(obj["viewset"]),
                )
            else:
                setattr(
                    viewset,
                    action,
                    method_decorator(
                        name=action,
                        decorator=swagger_auto_schema(tags=tags),
                    )(obj["viewset"]),
                )
        return viewset

    return decorator
