from django.shortcuts import render
from django.utils.text import capfirst
from rest_framework import status, viewsets
from utils.make_response import response as Response
from utils.pagination import BasePagination

class BaseModelViewSet(viewsets.ModelViewSet):
    http_method_names = ["get", "post", "patch", "delete"]
    response_message = ""
    status_code = ""
    pagination_class = BasePagination

    def get_model_name(self):
        """
        The function `get_model_name` returns the model name in a readable format by capitalizing the
        first letter.
        :return: The method `get_model_name` is returning the model name in a readable format by
        capitalizing the first letter of the model's verbose name.
        """
        """
        Method to get the model name in a readable format.
        Override this method if you want a different model name representation.
        """
        return capfirst(self.queryset.model._meta.verbose_name)

    def get_message(self, request, *args, **kwargs):
        """
        The function `get_message` generates a dynamic message based on the request method and model
        name.

        :param request: The `request` parameter in the `get_message` method represents the HTTP request
        made to the server. It contains information about the request type (GET, POST, PATCH, DELETE),
        any data sent with the request, headers, and other relevant details. The method uses the
        `request.method` attribute
        :return: The method is returning a dynamic message based on the HTTP method of the request and
        the model name. The specific message returned depends on the request method:
        """
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
        """
        The `create` function overrides the default behavior to return a custom response with a message
        and status code.

        :param request: The `request` parameter in the `create` method represents the HTTP request that
        is being made to create a new resource. It contains information such as the request method,
        headers, data, and other details related to the request being processed by the API endpoint
        :return: The `create` method is returning a Response object with the data from the super class
        method call, a message obtained from the `get_message` method, and a status code of 201
        (HTTP_CREATED).
        """
        response = super().create(request, *args, **kwargs)
        return Response(
            data=response.data,
            message=self.get_message(request, args, *kwargs),
            status_code=status.HTTP_201_CREATED,
        )

    def list(self, request, *args, **kwargs):
        """
        This Python function retrieves a list of objects based on query parameters and returns the
        serialized data along with a message and status code.

        :param request: The `request` parameter in the code snippet represents the HTTP request object
        that is received by the view. It contains information about the incoming request, such as query
        parameters, headers, and data. In this specific code snippet, the `request` object is used to
        extract query parameters using `request.query
        :return: The code snippet is returning a response with data from the serializer, a message
        obtained from the `get_message` method, and a status code of 200 (HTTP OK).
        """
        fields = request.query_params.get("fields")

        if fields:
            fields = tuple(field.strip() for field in fields.split(","))

        paginate_queryset = self.paginate_queryset(self.get_queryset())
        serializer = self.get_serializer(paginate_queryset, many=True, fields=fields)
        pagination_serializer = self.get_paginated_response(serializer.data)
        return Response(
            data=pagination_serializer.data,
            message=self.get_message(request, *args, **kwargs),
            status_code=status.HTTP_200_OK,
        )

    def retrieve(self, request, *args, **kwargs):
        """
        This Python function retrieves an object from the database, filters its fields based on query
        parameters, and returns a response with the filtered data.

        :param request: The `request` parameter in the `retrieve` method is typically an HTTP request
        object that contains information about the incoming request, such as query parameters, headers,
        and the request body. In this context, it is used to extract the query parameters, specifically
        the "fields" parameter, to dynamically filter
        :return: The code snippet is returning a response with the filtered data using a serializer with
        dynamic fields. The response includes the serialized data, a message obtained from the
        `get_message` method, and a status code of 200 (HTTP OK).
        """
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
        """
        The `partial_update` function overrides the default behavior to return a response with custom
        data, message, and status code.

        :param request: The `request` parameter in the `partial_update` method is typically an object
        that contains information about the current HTTP request, such as the request method, headers,
        data, and user authentication details. It is commonly used to extract data from the request,
        validate input, and perform operations based on the
        :return: The `partial_update` method is being overridden to return a custom response. It calls
        the parent class method `partial_update` and then constructs a new Response object with the data
        from the parent method, a custom message obtained from `self.get_message`, and a status code of
        206. This custom response is what is being returned by the `partial_update` method.
        """
        response = super().partial_update(request, *args, **kwargs)
        return Response(
            data=response.data,
            message=self.get_message(request, *args, **kwargs),
            status_code=206,
        )

    def destroy(self, request, *args, **kwargs):
        """
        This function overrides the destroy method to return a response with a message and status code.

        :param request: The `request` parameter in the `destroy` method is typically an object that
        represents the HTTP request made to the server. It contains information such as the request
        method (GET, POST, DELETE, etc.), headers, user authentication details, and any data sent in the
        request body. In this context
        :return: The `destroy` method is being called on the parent class using `super().destroy(request,
        *args, **kwargs)`, and then a `Response` object is being returned with a message obtained from
        `self.get_message(request, *args, **kwargs)` and a status code of `status.HTTP_204_NO_CONTENT`.
        """
        super().destroy(request, *args, **kwargs)
        return Response(
            message=self.get_message(request, *args, **kwargs),
            status_code=status.HTTP_204_NO_CONTENT,
        )


def handler404(request, exception):
    """
    The `handler404` function in Python returns a 404.html page with a status code of 404 for a given
    request.

    :param request: The `request` parameter in the `handler404` function is typically an HttpRequest
    object that represents the incoming HTTP request from the client. It contains information about the
    request, such as the requested URL, method (GET, POST, etc.), headers, and any data sent with the
    request. This parameter
    :param exception: The `exception` parameter in the `handler404` function is used to capture the
    exception that triggered the 404 error. This parameter allows you to handle the exception and
    customize the response accordingly when a 404 error occurs in your Django application
    :return: The `handler404` function is returning a rendered '404.html' template with a status code of
    404.
    """
    return render(request, "404.html", status=404)


def handler500(request):
    """
    The `handler500` function in Python renders a '500.html' template with a status code of 500.

    :param request: The `request` parameter in the `handler500` function is an object that represents
    the HTTP request made by the client to the server. It contains information about the request such as
    the URL, method, headers, and any data sent with the request. This parameter is typically passed to
    view functions in
    :return: The `handler500` function is returning a rendering of the '500.html' template with a status
    code of 500.
    """
    return render(request, "500.html", status=500)
