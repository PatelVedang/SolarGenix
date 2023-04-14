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

class CURL:
    x_content_type_options_regex = "X-Content-Type-Options: nosniff"
    windows7_regex = "Server: Microsoft-IIS/7.5"
    result = ""
    
    def main(self, target, regenerate):
        """
        This function contains a dictionary of handlers for different tool commands and executes the
        appropriate handler based on the input.
        """
        handlers = {
            'curl -I': [
                self.x_content_type_options_handler,
                self.unsupported_web_server_handler
            ],
            'default': default.default_handler
        }
        tool_cmd = target.tool.tool_cmd.strip()
        if handlers.get(tool_cmd):
            if regenerate or target.compose_result=="":
                self.result = ""
                for vul_handler in handlers[tool_cmd]:
                    vul_handler(target, regenerate)
                Target.objects.filter(id=target.id).update(compose_result=self.result)
                return self.result
            else:
                self.result = target.compose_result
                return self.result
        else:
            return handlers['default'](target, regenerate)

    def x_content_type_options_handler(self, target, regenerate):
        """
        This function checks if the X-Content-Type-Options header is missing and adds a vulnerability if
        it is.
        
        :param target: The target parameter is an object that represents the target website or web
        application being scanned for vulnerabilities. It likely contains information such as the URL,
        headers, and response data
        :param regenerate: A boolean variable that indicates whether the target's result should be
        regenerated or not. If it is True, the target's result will be regenerated
        """
        if regenerate or target.compose_result=="":
            if not re.search(self.x_content_type_options_regex, target.raw_result, re.IGNORECASE):
                error = "X-Content-Type-Options Header Missing"
                self.result += set_vul("CVE-2019-19089", error)
    
    def unsupported_web_server_handler(self, target, regenerate):
        """
        This function handles unsupported web servers by detecting if the server is obsolete and no
        longer maintained by its vendor or provider.
        
        :param target: The target parameter is an object that represents the web server being scanned.
        It contains information such as the IP address, port number, and protocol being used
        :param regenerate: A boolean value indicating whether the target should be regenerated or not
        """
        if regenerate or target.compose_result=="":
            if not re.search(self.x_content_type_options_regex, target.raw_result, re.IGNORECASE):
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
                    'cwe_id': 'N/A',
                    'cwe_name': 'N/A',
                    'solution': 'Remove the web server if it is no longer needed. Otherwise, upgrade to a supported version if possible or switch to another server.',
                    'sources': [
                    'N/A'
                    ],
                    'error': error
                }
                self.result += set_custom_vul(**data)

