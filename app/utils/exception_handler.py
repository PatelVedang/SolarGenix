import logging
import traceback
from collections import defaultdict

from rest_framework import status
from rest_framework.views import exception_handler

from .make_response import response

logger = logging.getLogger("django")


def custom_exception_handler(exc, context):
    """
    The function `custom_exception_handler` handles custom exceptions by mapping them to specific
    handlers and returning a response with the appropriate status code and message.

    :param exc: The `exc` parameter is the exception object that was raised. It contains information
    about the exception, such as its type, message, and traceback
    :param context: The `context` parameter in the `custom_exception_handler` function is a dictionary
    that contains information about the current request and view that raised the exception. It typically
    includes the following keys:
    :return: a response object.
    """
    try:
        traceback.print_exc()
        exception_class = exc.__class__.__name__
        handlers = {
            "NotAuthenticated": _handler_authentication_error,
            "InvalidToken": _handler_invalid_token_error,
            "ValidationError": _handler_validation_error,
            "AuthenticationFailed": _handler_authentication_failed_error,
        }
        res = exception_handler(exc, context)
        logger.error(str(exc))
        if exception_class in handlers:
            message = handlers[exception_class](exc, context, res)
        else:
            # if there is no handler is present
            message = str(exc)

        print(">" * 30, " " * 15, "Exception message start", " " * 15, "<" * 30)
        print("\n\n", message, "\n\n")
        print(">" * 30, " " * 15, "Exception message end", " " * 15, "<" * 30)
        print(">" * 30, " " * 15, "Exception class", " " * 15, "<" * 30)
        print("\n\n", exception_class, "\n\n")
        print(">" * 30, " " * 15, "Exception class end", " " * 15, "<" * 30)

        if exception_class == "ValidationError":
            return response(
                data=message,
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                message="validation errors",
            )
        return response(data={}, status_code=res.status_code, message=message)
    except Exception as e:
        logger.error(str(e))
        return response(data={}, status_code=500, message="Something went wrong.")


def _handler_authentication_error(exc, context, response):
    """
    The function returns a message indicating that an authorization token is not provided.

    :param exc: The `exc` parameter is the exception object that was raised during the authentication
    process
    :param context: The `context` parameter is a dictionary that contains additional information about
    the error that occurred. It can include details such as the request that caused the error, the user
    who made the request, or any other relevant information
    :param response: The `response` parameter is the HTTP response object that will be returned to the
    client. It contains information such as the status code, headers, and body of the response
    :return: the string "An authorization token is not provided."
    """
    return "An authorization token is not provided."


def _handler_authentication_failed_error(exc, context, response):
    try:
        value = exc.__dict__["detail"]["detail"]
    except Exception:
        value = str(exc)
    return value


def _handler_invalid_token_error(exc, context, response):
    """
    The function handles an invalid token error by returning a specific error message.

    :param exc: The `exc` parameter represents the exception that was raised. In this case, it would be
    an invalid token error
    :param context: The `context` parameter is a dictionary that contains additional information about
    the error that occurred. It can include details such as the request that caused the error, the user
    who made the request, or any other relevant information
    :param response: The `response` parameter is the HTTP response object that will be returned to the
    client. It contains information such as the status code, headers, and body of the response
    :return: the string "An authorization token is not valid."
    """
    return "An authorization token is not valid."


def default_value():
    return {
        "key": {"message": None, "code": None},  # Default for key
        "label": {"message": None, "code": None},  # Default for label
        "message": {"message": None, "code": None},  # Default for message
        "code": None,  # Default for code
    }


def _handler_validation_error(exc, context, response):
    """
    The function `_handler_validation_error` handles validation errors by extracting the error code and
    value, and returning a custom error message based on the code.

    :param exc: The `exc` parameter is an exception object that is raised when a validation error
    occurs. It contains information about the validation error
    :param context: The `context` parameter is a dictionary that contains additional information about
    the exception that occurred. It can include details such as the request, view, and args that were
    being processed when the exception occurred
    :param response: The `response` parameter is the response object that will be returned by the
    handler. It is used to modify the response if needed
    :return: a message based on the validation error code.
    """
    print(
        exc, "#" * 100
    )  # Print the exception for debugging along with a separator line

    error_dict = exc.get_full_details()  # Get the full error details as a dictionary
    errors_list = []  # Initialize an empty list to store formatted error details

    # Define a function to set default values for missing keys in the error data
    def default_value():
        return {
            "key": {"message": None, "code": None},  # Default structure for 'key'
            "label": {"message": None, "code": None},  # Default structure for 'label'
            "message": {
                "message": None,
                "code": None,
            },  # Default structure for 'message'
            "code": None,  # Default value for 'code'
        }

    try:
        # Iterate over each error field and its associated details in error_dict
        for key, value in error_dict.items():
            if isinstance(value, dict):  # Ensure the value is a dictionary
                # Use defaultdict to apply default values for missing keys
                error_data = defaultdict(default_value, value)
                # Extract relevant information from the error_data
                temp_dict = {
                    "key": error_data["key"]["message"],  # Extract message from 'key'
                    "code": error_data["message"][
                        "code"
                    ],  # Extract code from 'message'
                    "label": error_data["label"][
                        "message"
                    ],  # Extract message from 'label'
                    "message": error_data["message"][
                        "message"
                    ],  # Extract message from 'message'
                }

                # Append the formatted error data to the errors_list
                errors_list.append(temp_dict)

        # Print the final errors_list for debugging
        print(f"Output :\n\t{errors_list}")

    except KeyError as e:
        # Handle cases where a key is missing in the error dictionary
        print(f"KeyError encountered: {e}")
    except Exception as e:
        # Catch and handle any other unexpected exceptions
        print(f"An error occurred: {e}")
    # errors_list = {"error": errors_list}
    return {"errors": errors_list}  # Return the final list of formatted error details
