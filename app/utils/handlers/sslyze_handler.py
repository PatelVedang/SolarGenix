from scanner.models import *
from html import escape
import logging
logger = logging.getLogger('django')
import re
from datetime import datetime
from .default_handler import DEFAULT
default = DEFAULT()
from .cve import CVE
cve = CVE()
from .common_handler import *
import json
import asyncio

class SSLYSE:
    result = {}
    service_regex ="(\n\s+\*\s+|\\n\s+\*\s+|\\r\\n\s+\*\s+)(?P<service>[\w\s.]+):(\n|\\n|\\r\\n)"
    cert_regex = "Not After:\s+(?P<cert_expire_on>\d{4}-\d{2}-\d{2})"
    suites_regex = "The\s+server\s+accepted\s+the\s+following\s+(?P<suites>\d{1,})\s+cipher\s+suites:"
    services_objects = {}
    # service_regex = "\*(?P<service>[\w\s.]+):\\r\\n"
    
    async def handlers(self, tool_cmd, handlers, target, regenerate):
        jobs = []
        for vul_handler in handlers[tool_cmd]:
            jobs.append(vul_handler(target, regenerate))
        await asyncio.gather(*jobs)

    def main(self, target, regenerate):
        """
        This is a Python function that handles different tools and their corresponding handlers to
        generate results for a given target.
        
        :param target: The "target" parameter is an object that represents the target of a security
        assessment. It contains information about the target, such as its IP address, port number, and
        the tool to be used for the assessment
        :param regenerate: A boolean parameter that indicates whether the results should be regenerated
        or not. If set to True, the code will regenerate the results, otherwise it will use the
        previously generated results
        :return: either the result of the executed tool handlers or the result of the default handler,
        depending on the value of the `tool_cmd` parameter.
        """
        handlers = {
            'sslyze': [
                self.ssl_missing_handler,
                self.tls1_detect_handler,
                self.tls11_detect_handler,
                self.tls12_detect_handler
            ],
            'default': default.default_handler
        }
        tool_cmd = target.tool.tool_cmd.strip()
        if handlers.get(tool_cmd):
            if regenerate or not target.compose_result:
                self.result = {}
                self.services_objects = {}
                services = list(re.finditer(self.service_regex, target.raw_result))
                for service_obj in services:
                    index = services.index(service_obj)
                    if index != len(services)-1:
                        regex = f"(?s){service_obj.group()}(?P<content>.*?){services[index+1].group()}"
                        regex = regex.replace("\n","\\n").replace("\r","\\r").replace("\\n *", "\\n \*")
                        key = services[index].group().replace("\r\n","").replace("*","").strip()
                        value = re.search(regex, target.raw_result).groupdict().get('content')
                        self.services_objects = {**self.services_objects, **{key:value}}
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

    async def ssl_missing_handler(self, target, regenerate):
        """
        This function checks if an SSL certificate has expired and sets a vulnerability if it has.
        
        :param target: The target parameter is a variable that contains the result of a previous HTTP
        request to a website. It is assumed to contain the website's SSL certificate information
        :param regenerate: The `regenerate` parameter is not used in the given code snippet. It is not
        passed as an argument to any function or method. Therefore, its purpose is unknown
        """
        cert = re.search(self.cert_regex, target.raw_result)
        if cert:
            if cert.groupdict().get('cert_expire_on'):
                cert_expire_on = datetime.strptime(cert.groupdict().get('cert_expire_on'), '%Y-%m-%d')
                if cert_expire_on < datetime.utcnow():
                    error = "Expired SSL certificate"
                    evidence = self.services_objects.get('Certificates Information:', '')
                    vul_data = await alert_response(cve="CVE-2015-3886", error=error, tool="sslyze", alert_type=1, evidence=evidence)
                    self.result = {**self.result, **vul_data}
    
    async def tls1_detect_handler(self, target, regenerate):
        """
        This function detects if a target is using the TLS 1.0 protocol and flags it as a vulnerability.
        
        :param target: The target parameter is likely a string or object representing the target system
        or application that is being scanned for vulnerabilities. It could be an IP address, domain
        name, or other identifier
        :param regenerate: The "regenerate" parameter is not used in the code snippet provided. It is
        not defined or referenced anywhere in the function
        """
        if self.services_objects.get('TLS 1.0 Cipher Suites:'):
            search_result = re.search(self.suites_regex, self.services_objects['TLS 1.0 Cipher Suites:'])
            if search_result:
                if search_result.groupdict().get('suites') and int(search_result.groupdict().get('suites')) >= 1:
                    error = "TLS 1.0 Weak Protocol"
                    evidence = self.services_objects.get('TLS 1.0 Cipher Suites:', '')
                    vul_data = await alert_response(cve="CVE-2022-34757", error=error, tool="sslyze", alert_type=1, evidence=evidence)
                    self.result = {**self.result, **vul_data}
    
    async def tls11_detect_handler(self, target, regenerate):
        """
        This function detects if a remote service accepts connections encrypted using TLS 1.1 and
        provides information on the weaknesses of this protocol and a solution to enable support for TLS
        1.2 and/or 1.3.
        
        :param target: The target is the remote service that is being scanned for TLS 1.1 protocol
        support
        :param regenerate: The "regenerate" parameter is not used in the code snippet provided. It is
        not defined or referenced anywhere in the function
        """
        if self.services_objects.get('TLS 1.1 Cipher Suites:'):
            search_result = re.search(self.suites_regex, self.services_objects['TLS 1.1 Cipher Suites:'])
            if search_result:
                if search_result.groupdict().get('suites') and int(search_result.groupdict().get('suites')) >= 1:
                    complexity = "INFO"
                    error = "TLS 1.1 Weak Protocol"
                    desc = '''
                    The remote service accepts connections encrypted using TLS 1.1.
                    TLS 1.1 lacks support for current and recommended cipher suites.
                    Ciphers that support encryption before MAC computation, and authenticated encryption modes such as GCM cannot be used with TLS 1.1
                    
                    As of March 31, 2020, Endpoints that are not enabled for TLS 1.2 and higher will no longer function properly with major web browsers and major vendors.
                    '''
                    solution = "Enable support for TLS 1.2 and/or 1.3, and disable support for TLS 1.1."
                    evidence = self.services_objects.get('TLS 1.1 Cipher Suites:', '')
                    vul_data = await alert_response(
                        complexity=complexity,
                        error=error,
                        description=desc,
                        solution=solution,
                        tool="sslyze",
                        alert_type=4,
                        evidence=evidence
                    )
                    self.result = {**self.result, **vul_data}
    
    async def tls12_detect_handler(self, target, regenerate):
        """
        This function detects if a remote service accepts connections encrypted using TLS 1.2 and sets
        an information vulnerability accordingly.
        
        :param target: The target is the remote service that is being scanned for TLS 1.2 protocol
        support
        :param regenerate: The "regenerate" parameter is not used in the code snippet provided. It is
        not defined or referenced anywhere in the function
        """
        if self.services_objects.get('TLS 1.2 Cipher Suites:'):
            search_result = re.search(self.suites_regex, self.services_objects['TLS 1.2 Cipher Suites:'])
            if search_result:
                if search_result.groupdict().get('suites') and int(search_result.groupdict().get('suites')) >= 1:
                    evidence = self.services_objects.get('TLS 1.2 Cipher Suites:', '')
                    complexity = "INFO"
                    error = "TLS 1.2 Weak Protocol"
                    desc = 'The remote service accepts connections encrypted using TLS 1.2.'
                    solution = "N/A"
                    vul_data = await alert_response(
                        complexity=complexity,
                        error=error,
                        description=desc,
                        solution=solution,
                        tool="sslyze",
                        alert_type=4,
                        evidence=evidence
                    )
                    self.result = {**self.result, **vul_data}
