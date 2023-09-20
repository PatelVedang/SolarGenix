from scanner.models import *
from html import escape
import logging
logger = logging.getLogger('django')
import re
from .cve import CVE
cve = CVE()
from .default_handler import DEFAULT
default = DEFAULT()
from .common_handler import *
import json
import asyncio

class CURL:
    x_content_type_options_regex = "X-Content-Type-Options: nosniff"
    windows_regex = "Server: (?P<server>([\w\s-]*))(/(?P<version>\d+\.\d+(\.\d+)?))?"
    x_powered_by_in_header_regex = "X-Powered-By"
    server_in_header_regex = ".*Server:.*"

    result = {}
    
    async def handlers(self, tool_cmd, handlers, target, regenerate):
        """
        The function "handlers" takes in a tool command, a dictionary of handlers, a target, and a
        boolean flag, and creates a list of jobs to be executed concurrently using asyncio.
        
        :param tool_cmd: The `tool_cmd` parameter is a string that represents the command or tool being
        used. It is used to determine which handlers to execute for that specific command or tool
        :param handlers: The `handlers` parameter is a dictionary that contains the handlers for
        different tool commands. Each key in the dictionary represents a tool command, and the
        corresponding value is a list of handler functions for that command
        :param target: The "target" parameter is the target object or entity that the handlers will be
        applied to. It could be a website, a network, a file, or any other entity that the handlers are
        designed to work on
        :param regenerate: The `regenerate` parameter is a boolean value that indicates whether the
        target should be regenerated or not. It is used to control whether the vulnerability handlers
        should regenerate any necessary files or data related to the target before executing their tasks
        """
        jobs = []
        for vul_handler in handlers[tool_cmd]:
            jobs.append(vul_handler(target, regenerate))
        await asyncio.gather(*jobs)


    def main(self, target, regenerate):
        """
        This function contains a dictionary of handlers for different tool commands and executes the
        appropriate handler based on the input.
        """
        handlers = {
            'curl -I': [
                self.x_content_type_options_handler,
                self.unsupported_web_server_handler,
                self.server_in_response_header_handler,
                self.x_powered_by_in_response_header_handler
            ],
            'default': default.default_handler
        }
        tool_cmd = target.tool.tool_cmd.strip()
        if handlers.get(tool_cmd):
            if regenerate or not target.compose_result:
                self.result = {}
                
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.handlers(tool_cmd, handlers, target, regenerate))
                loop.close()

                Target.objects.filter(id=target.id).update(compose_result=self.result)
                return self.result
            else:
                self.result = target.compose_result
                return self.result
        else:
            return handlers['default'](target, regenerate)

    async def x_content_type_options_handler(self, target, regenerate):
        """
        This function checks if the X-Content-Type-Options header is missing and adds a vulnerability if
        it is.
        
        :param target: The target parameter is an object that represents the target website or web
        application being scanned for vulnerabilities. It likely contains information such as the URL,
        headers, and response data
        :param regenerate: A boolean variable that indicates whether the target's result should be
        regenerated or not. If it is True, the target's result will be regenerated
        """
        if not re.search(self.x_content_type_options_regex, target.raw_result, re.IGNORECASE):
            error = "X-Content-Type-Options Header Missing"
            vul_data = await alert_response(cve="CVE-2019-19089", error=error, tool=target.tool.tool_name, alert_type=1, evidence=self.x_content_type_options_regex)
            self.result = {**self.result, **vul_data}
    
    async def unsupported_web_server_handler(self, target, regenerate):
        """
        This function handles unsupported web servers by detecting if the server is obsolete and no
        longer maintained by its vendor or provider.
        
        :param target: The target parameter is an object that represents the web server being scanned.
        It contains information such as the IP address, port number, and protocol being used
        :param regenerate: A boolean value indicating whether the target should be regenerated or not
        """
        # https://learn.microsoft.com/en-us/lifecycle/products/internet-information-services-iis reference of IIS 7.5
        search_result = re.search(self.windows_regex, target.raw_result, re.IGNORECASE)
        if search_result:
            server = search_result.groupdict().get('server').strip(" ").strip("\n") if search_result.groupdict().get('server') else ""
            version = search_result.groupdict().get('version').strip(" ").strip("\n") if search_result.groupdict().get('version') else ""


            server_objs = {
                'Microsoft-IIS':{
                    '6.0': datetime.strptime('14/07/2015',"%d/%m/%Y"),
                    '7.0': datetime.strptime('14/01/2020',"%d/%m/%Y"),
                    '7.5': datetime.strptime('14/01/2020',"%d/%m/%Y"),
                    '8.0': datetime.strptime('10/10/2023',"%d/%m/%Y"),
                    '8.1': datetime.strptime('10/01/2023',"%d/%m/%Y"),
                    '8.5': datetime.strptime('10/10/2023',"%d/%m/%Y"),
                    '10.0': datetime.strptime('12/01/2027',"%d/%m/%Y")
                },
                'Apache':{
                    '1.3': datetime.strptime('03/02/2010',"%d/%m/%Y"),
                    '2.0': datetime.strptime('10/07/2013',"%d/%m/%Y"),
                    '2.2': datetime.strptime('11/07/2017',"%d/%m/%Y"),
                    '2.4': datetime.strptime('10/10/2003',"%d/%m/%Y")
                }
            }
            if server_objs.get(server) and server_objs.get(server).get(version) and datetime.utcnow()>server_objs.get(server).get(version):
                error = "Unsupported Web Server Detection"
                data = {
                    'cve_id': 'N/A',
                    'description': 'According to its version, the remote web server is obsolete and no longer maintained by its vendor or provider.Lack of support implies that no new security patches for the product will be released by the vendor. As a result, it may contain security vulnerabilities.',
                    'cvvs3': {
                    'base_score': '10',
                    'error_type': 'CRITICAL'
                    },
                    'cvvs2': {
                    'base_score': '7.5',
                    'error_type': 'MEDIUM'
                    },
                    'cwe_ids': 'N/A',
                    'cwe_name': 'N/A',
                    'solution': 'Remove the web server if it is no longer needed. Otherwise, upgrade to a supported version if possible or switch to another server.',
                    'sources': [
                    'N/A'
                    ],
                    'error': error,
                    'tool': target.tool.tool_name,
                    'complexity': 'CRITICAL',
                    'alert_type':3,
                    'evidence': search_result.group()
                }
                vul_data = await alert_response(**data)
                self.result = {**self.result, **vul_data}

    async def server_in_response_header_handler(self, target, regenerate):
        """
        This function checks if the HTTP response header contains the server information and reports a
        vulnerability if it does.
        
        :param target: The target parameter is an object that represents the HTTP response received from
        the server. It contains information such as the response headers, status code, and response body
        :param regenerate: The "regenerate" parameter is not used in the code snippet provided. It is
        possible that it is defined elsewhere in the code or it is a placeholder for future
        implementation
        """
        search_result = re.search(self.server_in_header_regex, target.raw_result, re.IGNORECASE)
        if search_result:
            error = '''Server Leaks Version Information via "Server" HTTP Response Header Field'''
            vul_data = await alert_response(cve="CVE-2018-7844", error=error, tool=target.tool.tool_name, alert_type=1, evidence=search_result.group())
            self.result = {**self.result, **vul_data}

    async def x_powered_by_in_response_header_handler(self, target, regenerate):
        """
        This function checks if a server leaks information via the "X-Powered-By" HTTP response header
        and sets a vulnerability if it does.
        
        :param target: The target parameter is an object that represents the target of the vulnerability
        scan. It contains information such as the target URL, HTTP headers, and response body
        :param regenerate: The "regenerate" parameter is not used in the code snippet provided. It is
        possible that it is used in other parts of the code that are not shown
        """
        search_result = re.search(self.x_powered_by_in_header_regex, target.raw_result, re.IGNORECASE)
        if search_result:
            error = '''Server Leaks Information via "X-Powered-By" HTTP Response Header Field'''
            vul_data = await alert_response(cve="CVE-2018-7844", error=error, tool=target.tool.tool_name, alert_type=1, evidence=search_result.group())
            self.result = {**self.result, **vul_data}

