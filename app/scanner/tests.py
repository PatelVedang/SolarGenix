from user.tests import BaseAPITestCase
from scanner.models import Target, Tool

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
        obj = Target.objects.first()
        self._data = {
            "targets_id": [
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
        It tests the retrieve API endpoint for the Target app
        """
        self.login()
        self.insert_records()
        obj = Target.objects.first()
        self.set_response(self.client.get(f'{self.prefix}scan/{obj.id}/', format = "json"))
        self.match_success_response()


# It tests the CRUD operations of the Tool app.
class ToolTest(BaseAPITestCase):
    prefix = '/api/'

    def insert_records(self):
        """
        It creates a new record in the database with the tool_name and tool_cmd values
        """
        self._data = {
            "tool_name": "nmap",
            "tool_cmd": "nmap -Pn -sV"
        }
        self.set_response(self.client.post(f'{self.prefix}tool/', data=self._data , format = "json"))

    def test_create_api(self):
        """
        It logs in, inserts records, and matches the success response
        """
        self.login()
        self.insert_records()
        self.match_success_response()

    def test_update_api(self):
        """
        It updates the tool name and tool command of the first tool in the database.
        """
        self.login()
        self.insert_records()
        obj = Tool.objects.first()
        self._data = {
            "tool_name": "nmap v7.92",
            "tool_cmd": "nmap -Pn -sV"
        }
        self.set_response(self.client.patch(f'{self.prefix}tool/{obj.id}/', data= self._data, format="json"))
        self.match_success_response()

    def test_retrieve_api(self):
        """
        It tests the retrieve API endpoint for the Tool app
        """
        self.login()
        self.insert_records()
        obj = Tool.objects.first()
        self.set_response(self.client.get(f'{self.prefix}tool/{obj.id}/', format = "json"))
        self.match_success_response()

    def test_list_api(self):
        """
        It tests the list API of the tool app
        """
        self.login()
        self.set_response(self.client.get(f'{self.prefix}tool/', format = "json"))
        self.match_success_response()
    
    def test_delete_api(self):
        """
        It deletes the first record in the Tool table.
        """
        self.login()
        self.insert_records()
        obj = Tool.objects.first()
        self.set_response(self.client.delete(f'{self.prefix}tool/{obj.id}/', format = "json"))
        self.match_success_response()
    