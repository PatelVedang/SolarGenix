from rest_framework.exceptions import APIException


class CustomValidationError(APIException):
    """
    Custom exception class for handling validation errors in Django REST Framework.

    Attributes:
        status_code (int): HTTP status code to return (default: 400).
        default_detail (str): Default error message if none is provided.
        default_code (str): Default error code if none is provided.

    Args:
        detail (str, optional): Custom error message to return.
        code (str, optional): Custom error code to return.

    Example:
        raise CustomValidationError(detail="Invalid input.", code="invalid_input")
    """

    status_code = 400  # Set the desired HTTP status code
    default_detail = "A validation error occurred."  # Default error message
    default_code = "validation_error"  # Default error code

    def __init__(self, detail=None, code=None):
        if detail is not None:
            self.detail = detail
        else:
            self.detail = self.default_detail

        if code is not None:
            self.code = code
        else:
            self.code = self.default_code
