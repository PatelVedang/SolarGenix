from rest_framework.response import Response

def response(*args, **kwargs):
    status = kwargs.get("status", False)
    status_code = kwargs.get("status_code")
    message = kwargs.get("message")
    data = kwargs.get("data")
    result =  {"status_code":status_code, "status":status, "message":message, "data": data}
    return Response(result, status=status_code)