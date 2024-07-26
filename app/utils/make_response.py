from rest_framework.response import Response


def response(*args, **kwargs):
    """
    The function `response` returns a `Response` object with the provided status code, message, and
    data.
    :return: a Response object with the provided status code, message, and data.
    """
    status_code = kwargs.get("status_code")
    message = kwargs.get("message", "")
    data = kwargs.get("data", {})
    result = {"message": message, "data": data}
    return Response(result, status=status_code)
