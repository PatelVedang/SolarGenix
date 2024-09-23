from rest_framework.exceptions import APIException


class CustomValidationError(APIException):
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
