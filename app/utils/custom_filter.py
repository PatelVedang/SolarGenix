from django.db.models import Q, QuerySet, Model, Field
from django.http.request import QueryDict
from typing import Type
from ast import literal_eval


def filter_model(
    query_params: QueryDict, queryset: QuerySet[Model], model: Type[Model]
):
    """
    Filter the given queryset based on the provided query parameters.

    Args:
        query_params (QueryDict): A QueryDict containing the query parameters.
        queryset (QuerySet[Model]): The queryset to be filtered.
        model (Type[Model]): The model class.

    Returns:
        QuerySet[Model]: The filtered queryset.
    """

    filter_q = Q()
    sorting = query_params.get("sort")
    print("➡ utils/custom_filters.py:23 sorting:", sorting)
    select_fields = query_params.get("select")
    print("➡ utils/custom_filters.py:25 select_fields:", select_fields)
    search_fields_param = query_params.get("search_fields")
    print("Search", search_fields_param)

    # Handle search filter
    search_param = query_params.get("search")
    print("search_param", search_param)
    if search_param:
        if search_fields_param:
            search_fields = [
                field.strip()
                for field in search_fields_param.split(",")
                if field.strip()
            ]
        else:
            search_fields = [
                f.name
                for f in model._meta.get_fields()
                if isinstance(f, Field) and not f.is_relation
            ]
        search_q = Q()
        for field in search_fields:
            search_q |= Q(**{f"{field}__icontains": search_param})
        filter_q &= search_q

    for key, value in query_params.items():
        if key not in ["sort", "search"]:
            field_parts = key.split("__")
            field = field_parts[0]
            lookup_type = field_parts[1] if len(field_parts) > 1 else None

            if any(f.name == field for f in model._meta.get_fields()):
                # Add logic to handle nested lookups
                if len(field_parts) > 2:
                    nested_lookup = "__".join(field_parts[1:])
                    filter_expr = f"{field}__{nested_lookup}"
                else:
                    filter_expr = f"{field}__{lookup_type}" if lookup_type else field

                if lookup_type == "not_in":
                    filter_expr = f"{field}__in"
                    lookup = [val.strip() for val in value.split(",") if val.strip()]
                    filter_q &= ~Q(**{filter_expr: lookup})
                else:
                    lookup = (
                        [
                            val.strip() for val in value.split(",") if val.strip()
                        ]  # Split values by comma and strip whitespace
                        if isinstance(value, str) and lookup_type == "in"
                        else [
                            literal_eval(val)
                            if isinstance(val, str) and val.startswith("[")
                            else val
                            for val in value
                        ]
                        if isinstance(value, list)
                        else literal_eval(value)
                        if isinstance(value, str) and value.startswith("[")
                        else value
                    )
                    filter_q &= Q(**{filter_expr: lookup})

    if select_fields:
        select_fields = [
            field.strip() for field in select_fields.split(",") if field.strip()
        ]
        queryset = queryset.values(*select_fields)

    if sorting:
        sort_fields = {field.strip() for field in sorting.split(",") if field.strip()}
        queryset = queryset.order_by(*sort_fields)

    queryset = queryset.filter(filter_q)
    return queryset
