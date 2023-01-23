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

# It tests the API endpoints of the Tool app.
class ScanTest(BaseAPITestCase):
    prefix = '/api/'

    def insert_records(self):
        """
        It creates a tool record, then creates a scan record with the tool_id and two ip addresses
        """
        self._data = {
            "tool_name": "nmap",
            "tool_cmd": "nmap -Pn -sV"
        }
        self.set_response(self.client.post(f'{self.prefix}tool/', data=self._data , format = "json"))
        tool_id = self._data.get('data').get('id')
        self._data = {
            "ip": [
                "20.220.195.124","20.220.195.124"
            ],
            "tools_id": [
                tool_id
            ]
        }
        self.set_response(self.client.post(f'{self.prefix}scan/', data=self._data , format = "json"))
    
    def test_list_api(self):
        """
        It tests the list API of the scan app
        """
        self.login()
        self.insert_records()
        self.set_response(self.client.get(f'{self.prefix}scan/', format = "json"))
        self.match_success_response()
       

    def test_create_api(self):
        """
        It creates some machine records, and then matches the response
        """
        self.login()
        self.insert_records()
        self.match_success_response()
    
    def test_add_by_ids_api(self):
        """
        It logs in, inserts records, gets the first record, sets the data, sets the response, and
        matches the success response
        """
        self.login()
        self.insert_records()
        obj = Machine.objects.first()
        self._data = {
            "machines_id": [
                obj.id
            ]
        }
        self.set_response(self.client.post(f'{self.prefix}scan/addByIds/', data=self._data , format = "json"))
        self.match_success_response()
    
    def test_add_by_numbers_api(self):
        """
        It tests the API endpoint `/scan/addByNumbers/` by sending a POST request with the data
        `{"count": 5}` and checks if the response is successful
        """
        self.login()
        self.insert_records()
        self._data = {
            "count": 5
        }
        self.set_response(self.client.post(f'{self.prefix}scan/addByNumbers/', data=self._data , format = "json"))
        self.match_success_response()
    
    def test_retrieve_api(self):
        """
        It tests the retrieve API endpoint for the Machine app
        """
        self.login()
        self.insert_records()
        obj = Machine.objects.first()
        self.set_response(self.client.get(f'{self.prefix}scan/{obj.id}/', format = "json"))
        self.match_success_response()

    