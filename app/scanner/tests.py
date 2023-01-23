from user.tests import BaseAPITestCase
from scanner.models import Machine, Tool

# It tests the exception handlers
class ExceptionHandlerTest(BaseAPITestCase):
    prefix = '/api/'

    def test_unauthorize(self):
        """
        It tests the unauthorize exception handler.
        """
        self.set_response(self.client.get(f'{self.prefix}scan/'))
        self.match_error_response()

    def test_invalid_token(self):
        """
        It tests the invalid token exception.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer unittest")
        self.set_response(self.client.get(f'{self.prefix}scan/', format = "json"))
        self.match_error_response()


    def test_not_found_error(self):
        """
        It tests the error response when a record is not found.
        """
        self.login()
        self.set_response(self.client.get(f'{self.prefix}scan/0/', format = "json"))
        self.match_error_response()

    def test_validation_error(self):
        """
        It tests the validation error.
        """
        self.login()
        self._data = {
            "ip": [
                "string"
            ]
        }
        self.set_response(self.client.post(f'{self.prefix}scan/', data=self._data, format = "json"))
        self.match_error_response()
