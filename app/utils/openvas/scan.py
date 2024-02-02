import requests
import argparse
import json
import time
import socket
from tldextract import extract
import traceback
import pandas as pd
from datetime import datetime
import signal
from django.conf import settings


class openVAS:

    base_url = settings.OPENVAS_API_SERVER
    username = settings.OPENVAS_ROOT_USER
    password = settings.OPENVAS_ROOT_USER_PASSWORD

    def __init__(self, url, timeout):
        """
        The above function initializes an object with a given URL and timeout, extracts the IP address
        from the URL, sets prerequisites for openVAS, and performs a login operation.
        
        :param url: The `url` parameter is the URL of the domain you want to connect to. It is used to
        extract the IP address of the domain and set it as the `ip` attribute
        :param timeout: The `timeout` parameter is used to set the maximum time (in seconds) that the
        program will wait for a response from the server before timing out. It is passed as an argument
        to the `__init__` method of the class
        """
        # Getting ip from url
        try:
            self.ip = ".".join(list(extract(url))).strip(".")
            self.ip = socket.gethostbyname(self.ip)
        except:
            raise Exception("Invalid domain")
        
        # Setting prerequisites for openVAS
        self.url = url
        self.timeout_limit = timeout
        

        # Login
        print("#"*10, f"Login", "#"*10)
        res = self.login()
        data = self.get_res_data(res)
        if self.is_200(res):
            
            # Setting headers
            self.get_req_headers = {
                'Authorization': f"Bearer {data.get('data',{}).get('access','')}"
            }
            self.post_req_headers = {
                'Content-Type': 'application/json',
                'Authorization': f"Bearer {data.get('data',{}).get('access','')}"
            }

        else:
            raise Exception("There is no user named you in openVAS.")
        print("Successfully login with openVAS")

                        
    def current_timestamp(self):
        """
        The function returns the current timestamp in the format "day-month-year_hour:minute:second".
        :return: The current timestamp in the format "day-month-year_hour:minute:second".
        """
        return datetime.strftime(datetime.utcnow(),"%d-%B-%Y_%H:%M:%S")


    def getRequest(self, sub_url, is_auth):
        """
        The function `getRequest` sends a GET request to a specified sub_url, with optional
        authentication, and returns the response.
        
        :param sub_url: The `sub_url` parameter is a string that represents the endpoint or path of the
        URL that you want to send a GET request to. It is appended to the `base_url` to form the
        complete URL
        :param is_auth: The `is_auth` parameter is a boolean value that indicates whether the request
        should be made with authentication or not. If `is_auth` is `True`, the request will include the
        headers specified by `self.get_req_headers`. If `is_auth` is `False`, the request will be made
        :return: a GET request using the requests library. If `is_auth` is True, it includes the headers
        from `self.get_req_headers` in the request. The function returns the response object from the
        request.
        """
        if is_auth:
            return requests.request("GET", f"{self.base_url}{sub_url}", headers=self.get_req_headers)
        else:
            return requests.request("GET", f"{self.base_url}{sub_url}")
    
    def deleteRequest(self, sub_url):
        """
        The function sends a DELETE request to a specified sub URL using the base URL and request
        headers.
        
        :param sub_url: The `sub_url` parameter is a string that represents the specific endpoint or
        resource that you want to delete. It is appended to the `base_url` to form the complete URL for
        the DELETE request
        :return: the response object from the DELETE request made using the requests library.
        """
        return requests.request("DELETE", f"{self.base_url}{sub_url}", headers=self.get_req_headers)
    

    def postRequest(self, sub_url, payload, is_auth, only_auth=False):
        """
        The function `postRequest` sends a POST request to a specified URL with the given payload and
        headers, depending on the authentication status.
        
        :param sub_url: The `sub_url` parameter is the endpoint or path of the URL where the POST
        request will be sent. It is appended to the `base_url` to form the complete URL for the request
        :param payload: The `payload` parameter is the data that you want to send in the POST request.
        It can be a dictionary, a list of tuples, or a string. The data will be sent as the body of the
        request
        :param is_auth: The `is_auth` parameter is a boolean value that indicates whether the request
        requires authentication. If `is_auth` is `True`, it means the request requires authentication.
        If `is_auth` is `False`, it means the request does not require authentication
        :param only_auth: The `only_auth` parameter is a boolean flag that indicates whether the request
        should only be made with authentication headers. If `only_auth` is set to `True`, the request
        will be made with the `get_req_headers` headers. If `only_auth` is set to `False` or, defaults
        to False (optional)
        :return: a POST request using the requests library. The returned value is the response object
        from the request.
        """
        if is_auth and not only_auth:
            return requests.request("POST", f"{self.base_url}{sub_url}", data=payload, headers=self.post_req_headers)
        elif is_auth and only_auth:
            return requests.request("POST", f"{self.base_url}{sub_url}", data=payload, headers=self.get_req_headers)
        else:
            return requests.request("POST", f"{self.base_url}{sub_url}", data=payload)

    def is_200(self, res):
        """
        The function checks if the status code of a response is 200 and returns True if it is, otherwise
        it returns False.
        
        :param res: The parameter "res" is expected to be an object that represents a response from a
        web request. It is assumed to have a property called "status_code" which represents the HTTP
        status code of the response
        :return: a boolean value. If the status code of the response is 200, it will return True.
        Otherwise, it will return False.
        """
        if res.status_code == 200:
            return True
        else:
            return False
        
    def is_400(self, res):
        """
        The function checks if the status code of a response is 400 and returns True if it is, otherwise
        it returns False.
        
        :param res: The parameter "res" is expected to be an object that represents a response from a
        web request. It is assumed to have a property called "status_code" that represents the HTTP
        status code of the response
        :return: a boolean value. If the status code of the response is 400, it will return True.
        Otherwise, it will return False.
        """
        if res.status_code == 400:
            return True
        else:
            return False
        
    def is_409(self, res):
        """
        The function checks if the status code of a response is 409 and returns True if it is, otherwise
        it returns False.
        
        :param res: The parameter "res" is expected to be an object that represents a response from a
        HTTP request. It is assumed to have a property called "status_code" which represents the HTTP
        status code of the response
        :return: a boolean value. If the status code of the response is 409, it will return True.
        Otherwise, it will return False.
        """
        if res.status_code == 409:
            return True
        else:
            return False
    
    def is_500(self, res):
        """
        The function checks if the status code of a response is 500 and returns True if it is, otherwise
        it returns False.
        
        :param res: The parameter "res" is expected to be an object that represents a response from a
        web request. It is assumed to have a property called "status_code" which represents the HTTP
        status code of the response
        :return: a boolean value. If the status code of the response is 500, it will return True.
        Otherwise, it will return False.
        """
        if res.status_code == 500:
            return True
        else:
            return False

    def get_res_data(self, res):
        """
        The function `get_res_data` takes a response object `res` and returns the JSON data from the
        response, or an empty dictionary if an exception occurs.
        
        :param res: The parameter "res" is expected to be a response object from a HTTP request
        :return: the result of parsing the response text as JSON using the `json.loads()` function. If
        an exception occurs during this process, the function will print the traceback and return an
        empty dictionary.
        """
        try:
            return json.loads(res.text)
        except Exception as e:
            traceback.print_exc()
            return {}
        
    def login(self):
        """
        The `login` function sends a POST request to the "/api/auth/login" endpoint with the provided
        username and password.
        :return: The login function is returning the result of a post request to the "/api/auth/login"
        endpoint with the provided payload.
        """
        payload = {
            'username': self.username,
            'password': self.password
        }
        return self.postRequest("/api/auth/login", payload, False)
        
    def create_target(self):
        """
        The function creates a target by sending a POST request with a JSON payload containing the
        target's name, port list, and hosts.
        :return: the result of the `postRequest` method with the parameters `"/api/targets/"`,
        `payload`, and `True`.
        """
        payload = json.dumps({
            "name": self.url,
            "portList": "4a4717fe-57d2-11e1-9a26-406186ea4fc5",
            "hosts": [
                self.ip
            ]
        })
        return self.postRequest("/api/targets/", payload, True)
    
    def get_targets(self):
        """
        The function `get_targets` makes a GET request to the "/api/targets/" endpoint and returns the
        response.
        :return: the result of a GET request to the "/api/targets/" endpoint.
        """
        return self.getRequest("/api/targets/", True)
    
    def get_target(self, id):
        """
        The function `get_target` retrieves a target with a specific ID from an API.
        
        :param id: The "id" parameter is the unique identifier of the target that you want to retrieve
        information for
        :return: the result of a GET request to the API endpoint "/api/targets/{id}/" with the parameter
        "id" passed in. The second parameter "True" indicates that the request should be authenticated.
        """
        return self.getRequest(f"/api/targets/{id}/", True)
    
    def get_target_by_name(self):
        """
        The function `get_target_by_name` retrieves the ID of a target record based on its name.
        :return: the ID of the target record that matches the given URL.
        """
        res = self.get_targets()
        targets = self.get_res_data(res)
        if self.is_200(res):
            df = pd.DataFrame(targets.get('data',{}))
            record = df[df['name'] == self.url]
            if len(record):
                return record['id'].values[0]
            else:
                raise Exception(f"Target record does not exist with url:{self.url}")
        else:
            raise Exception(targets.get('message',f"Target record does not exist with url:{self.url}"))
        

    def create_task(self, target_id):
        payload = {
            'name': self.url,
            'target': target_id,
            'config': 'daba56c8-73ec-11df-a475-002264764cea',
            'scanner': '08b69003-5fc2-4037-a479-93b440211c73'
        }
        return self.postRequest("/api/tasks/", payload, True, True)
    
    def get_task(self, id):
        """
        The function `get_task` retrieves a task with a specific ID from an API.
        
        :param id: The `id` parameter is the unique identifier of the task that you want to retrieve
        :return: the result of a GET request to the API endpoint "/api/tasks/{id}/".
        """
        return self.getRequest(f"/api/tasks/{id}/", True)
    
    def delete_task(self, id):
        """
        The function deletes a task with a specified ID.
        
        :param id: The `id` parameter is the unique identifier of the task that you want to delete. It
        is used to specify which task should be deleted from the system
        :return: The deleteRequest method is being called and the result of that method is being
        returned.
        """
        return self.deleteRequest(f"/api/tasks/{id}/")

    def get_task_status(self, id):
        """
        The function `get_task_status` retrieves the task status for a given task ID.
        
        :param id: The `id` parameter is the unique identifier of the task for which you want to
        retrieve the task status
        :return: the result of a GET request to the API endpoint "/api/tasks/{id}/taskStatus/".
        """
        return self.getRequest(f"/api/tasks/{id}/taskStatus/", True)
    
    def start_task(self, id):
        """
        The function "start_task" sends a request to start a task with a specific ID.
        
        :param id: The "id" parameter is the unique identifier of the task that you want to start. It is
        used to specify which task you want to perform the action on
        :return: the result of the `getRequest` method with the URL `/api/tasks/{id}/startTask/` and the
        parameter `True`.
        """
        return self.getRequest(f"/api/tasks/{id}/startTask/", True)
    
    def stop_task(self, id):
        """
        The function `stop_task` sends a GET request to stop a specific task identified by its ID.
        
        :param id: The "id" parameter is the unique identifier of the task that you want to stop. It is
        used to specify which task should be stopped
        :return: the result of the `getRequest` method with the endpoint `/api/tasks/{id}/stopTask/` and
        the boolean value `True` as arguments.
        """
        return self.getRequest(f"/api/tasks/{id}/stopTask/", True)
    
    def get_report_result(self, task_id):
        """
        The function `get_report_result` retrieves a completed report for a given task ID.
        
        :param task_id: The `task_id` parameter is the unique identifier for a specific task. It is used
        to retrieve information about the task and generate a report based on that task
        :return: the text content of a report if it meets certain conditions. If there is no completed
        report available for the given task, it raises an exception. If there is an error in the
        response, it raises an exception with the error message.
        """
        
        res = self.get_task(task_id)
        data = self.get_res_data(res)
        for i in range(round(round(float(settings.OPENVAS_REPORT_GEN_TIMEOUT))/round(float(settings.OPENVAS_REPORT_GEN_DELAY)))):
            if data['data']['report_count']['finished'] == "1" and data['data']['status']=="Done":
                break
            else:
                time.sleep(round(float(settings.OPENVAS_REPORT_GEN_DELAY)))
                res = self.get_task(task_id)
                data = self.get_res_data(res)
                continue

        if self.is_200(res):
            if data['data']['report_count']['finished'] == "1" and data['data']['status']=="Done":
                report_id = data['data']['last_report']['report']['id']
                payload = {
                    "report_id": report_id,
                    "filters": "apply_overrides=0 levels=hml rows=-1 min_qod=70 first=1 sort-reverse=severity notes=1 overrides=1",
                    "format": "TXT"
                }
                response = self.postRequest("/api/reports/downloadReport/", payload, True, True)
                return response.text
            else:
                raise Exception(f"There is no completed report available for task {self.url}")
        else:
            raise Exception(data.get('message',''))
    
    def set_report_result(self, task_id):
        """
        The function saves the result of a report in a text file with a specific file name.
        
        :param task_id: The `task_id` parameter is the identifier of a task in the OpenVAS system. It is
        used to retrieve the result of a specific task
        """
        res_str = self.get_report_result(task_id)
        file_path = f"openVAS_{self.url}_{self.current_timestamp()}.txt"
        with open(file_path, 'w') as file:
            file.write(res_str)
        print(f"output is saved in the file {file_path} in same folder where this script is located.")

    def add_margin(self):
        print("\n\n")

    def main(self):
        """
        The main function performs a series of tasks including adding a target, adding a task, starting
        the task, monitoring the task's progress, and generating a report.
        :return: The function `main` is returning the result of the `get_report_result` method call.
        """
        start_time = datetime.utcnow()

        # Setting timeout limit
        signal.signal(signal.SIGALRM, lambda signum, frame: self.timeout_handler(signum, frame))
        signal.alarm(self.timeout_limit)
        
        # Add target
        self.add_margin()
        print("#"*10, f"Adding new target for url: {self.url}", "#"*10)
        res = self.create_target()
        target_data = self.get_res_data(res)
        if self.is_200(res):
            target_id = target_data.get('data',{}).get('id',"")
        elif self.is_409(res):
            print(f"Target with url:{self.url} is already present")
            print(f"Getting target {self.url} from exiting targets")
            target_id = self.get_target_by_name()
            print(f"Target found with url:{self.url}")
        else:
            raise Exception(target_data.get('message',''))
        print(f"Target addedd successfully with id:{target_id}")
        
        # Adding Task
        self.add_margin()
        print("#"*10, f"Adding new task for url: {self.url}", "#"*10)
        res = self.create_task(target_id)
        task_data = self.get_res_data(res)
        if self.is_200(res):
            task_id = task_data.get('data',{}).get('id',"")
        else:
            raise Exception(task_data.get('message',''))
        print(f"Task addedd successfully with id:{task_id}")
        
        # Setting new signals to handle scan timeout
        signal.alarm(0)
        before_scan_start_time = round((datetime.utcnow()-start_time).total_seconds())
        self.timeout_limit = self.timeout_limit - before_scan_start_time

        # Manually calling timeout hanlder
        if self.timeout_limit <= 0:
            self.timeout_handler(signal.SIGALRM, None, task_id)

        signal.signal(signal.SIGALRM, lambda signum, frame: self.timeout_handler(signum, frame, task_id))
        signal.alarm(self.timeout_limit)


        # Start Task
        self.add_margin()
        print("#"*10, f"Starting task with id:{task_id}", "#"*10)
        res = self.start_task(task_id)
        task_data = self.get_res_data(res)
        if self.is_200(res):
            # task_id = task_data.get('data',{}).get('id',"")
            print("Task started sucessfully!")
        else:
            raise Exception(task_data.get('message',''))

        # Get realtime status
        self.add_margin()
        print("#"*10, f"Gathering Real Time Status for task: {task_id}", "#"*10)
        while True:
            res = self.get_task_status(task_id)
            task_progress_data = self.get_res_data(res)
            if self.is_200(res):
                progress = task_progress_data.get('data',{}).get('progress')
                status = task_progress_data.get('data',{}).get('status')
                try:
                    if int(progress) < 100 and status!='Done':
                        print(f"Scan completed {progress}% for url {self.url}")
                        time.sleep(2)
                        continue
                    else:
                        print(f"Scan completed {progress}% for url {self.url}")
                        break
                except TimeoutError as e:
                    raise Exception(str(e))
                except Exception as e:
                    raise Exception(f"Failed to get task status : HTTP/{res.status_code}", "\n", f"Error: {task_progress_data.get('message')}")
            else:
                raise Exception(f"Failed to get task status : HTTP/{res.status_code}", "\n", f"Error: {task_progress_data.get('message')}")
            
        # time.sleep(10)

        # Generate Report
        self.add_margin()
        print("#"*10, "Generating Report", "#"*10)
        return self.get_report_result(task_id)

    def timeout_handler(self, signum, frame, task_id=None):
        """
        The function `timeout_handler` handles a timeout event by stopping and deleting a task, and then
        raising a `TimeoutError`.
        
        :param signum: The `signum` parameter in the `timeout_handler` function represents the signal
        number that caused the timeout. In this case, it is used to handle the `SIGALRM` signal, which
        is typically raised when a timeout occurs
        :param frame: The `frame` parameter is a reference to the current stack frame at the time the
        signal was received. It contains information about the current execution context, such as the
        code being executed and the values of local variables
        :param task_id: The `task_id` parameter is an optional identifier for a specific task. It is
        used to identify and manage tasks within the `timeout_handler` function
        """
        if task_id:
            self.stop_task(task_id)
            print("#"*10, f"Task {task_id} was terminated.", "#"*10)
            self.delete_task(task_id)
            print("#"*10, f"Task {task_id} was deleted.", "#"*10)
        raise TimeoutError("Timeout occurred")


# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(description="openVAS Scan Argument Parser")
#     parser.add_argument('--url', type=str, help='Specify the URL to scan', required=True)
#     parser.add_argument('--timeout', type=int, help='Specify the scan timeout limit for openVAS', required=True)
#     args = parser.parse_args()
#     url = args.url
#     timeout = args.timeout
#     # username = "parimal.patel"
#     username = "parimal1"
#     password = "Parimal@1234"
    # gvm = openVAS(url, timeout)
#     gvm.main()


    

    


