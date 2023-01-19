from rest_framework.views import exception_handler
from .make_response import response

def custom_exception_handler(exc, context):
    try:
        exception_class = exc.__class__.__name__
        print(">"*30," "*15,"Exception message start", " "*15,"<"*30)
        print("\n\n",str(exc), "\n\n")
        print(">"*30," "*15,"Exception message end", " "*15,"<"*30)
        print(">"*30," "*15,"Exception class", " "*15,"<"*30)
        print("\n\n",exception_class, "\n\n")
        print(">"*30," "*15,"Exception class end", " "*15,"<"*30)

        handlers = {
            'NotAuthenticated' : _handler_authentication_error,
            'InvalidToken' : _handler_invalid_token_error,
            'ValidationError' : _handler_validation_error,
        }
        res = exception_handler(exc,context)
        if exception_class in handlers:
            message = handlers[exception_class](exc, context, res)
        else:
            message = str(exc)
        
        return response(status=False, data={}, status_code= res.get('status_code',401) if res else 401, message=message)
    except Exception as e:
        print(e)


def _handler_authentication_error(exc, context, response):
    return "Authorization token not provided."

def _handler_invalid_token_error(exc, context, response):
    return "Authorization token not valid."

def _handler_validation_error(exc, context, response):
    key = list(list(exc.__dict__.values())[0].keys())[0]
    code = list(list(exc.__dict__.values())[0].values())[0][0].__dict__['code']
    value = list(list(exc.__dict__.values())[0].values())[0][0]

    custom_msg_code = ["required", "null", "blank"]
    if code in custom_msg_code:
        message = f"{key} field is required"
    elif code:
        message = f"{value}"
    return message