from scanner.models import *
from html import escape
import logging
logger = logging.getLogger('django')
import re
import requests
from distutils.version import StrictVersion
from bs4 import BeautifulSoup
from .cve import CVE
cve = CVE()
from .default_handler import DEFAULT
default = DEFAULT()
from .common_handler import *

# The NIKTO class contains a method for handling the absence of an anti-clickjacking X-Frame-Options
# header in a target's raw result.
class NIKTO:
    anti_clickjacking_regex = "The anti-clickjacking X-Frame-Options header is not present."
    asp_version_regex = "Retrieved x-aspnet-version header: (?P<version>\d+\.\d+(\.\d+)?)"

    def main(self, target, regenerate):
        """
        This function selects a handler based on the tool command and executes it with the given target
        and regenerate parameters.
        
        :param target: The "target" parameter is an object that contains information about the target
        being scanned, such as its URL, IP address, and other relevant details. It is passed as an
        argument to the main function
        :param regenerate: The `regenerate` parameter is a boolean value that indicates whether or not
        to regenerate the output of the tool being used. If `regenerate` is `True`, the output will be
        regenerated, otherwise the existing output will be used
        :return: the result of calling one of two possible handlers, depending on the value of
        `tool_cmd`. If `tool_cmd` is equal to `'nikto -host'`, it will call the
        `anti_clickjacking_handler` function with the `target` and `regenerate` arguments. Otherwise, it
        will call the `default_handler` function with the same arguments. The result
        """
        handlers = {
            'nikto -host': [
                self.anti_clickjacking_handler,
                self.jquery_handler,
                self.jquery_detection_handler,
                self.asp_version_handler
            ],
            'default': default.default_handler
        }
        tool_cmd = target.tool.tool_cmd.strip()
        if handlers.get(tool_cmd):
            regenerate =True
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

    def anti_clickjacking_handler(self, target, regenerate):
        """
        This function checks for the presence of an anti-clickjacking header and sets a vulnerability if
        it is missing.
        
        :param target: The `target` parameter is an object that represents the target website or web
        application that is being scanned for vulnerabilities. It likely contains information such as
        the URL, HTTP headers, and response data
        :param regenerate: A boolean parameter that indicates whether the result should be regenerated
        or not. If set to True, the function will regenerate the result even if it already exists. If
        set to False, the function will return the existing result without regenerating it
        :return: the value of the "result" variable, which is either an empty string or a string
        containing a vulnerability message.
        """
        
        if re.search(self.anti_clickjacking_regex, target.raw_result, re.IGNORECASE):
            error = "Missing Anti-clickjacking Header"
            self.result += set_vul("CVE-2018-17192", error)
    
    def jquery_handler(self, target, regenerate):
        """
        This function checks if a website is using a vulnerable version of jQuery and reports it as a
        potential XSS vulnerability.
        
        :param target: The target parameter is an object that contains information about the target
        website, including its IP address
        :param regenerate: The "regenerate" parameter is not used in the given code snippet. It is not
        clear what its purpose is without further context
        """
        try:
            url = f'http://{target.ip}'
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            jquery_script = soup.find('script', src=lambda src: src and 'jquery' in src)

            if jquery_script:
                jquery_url = jquery_script['src']
                if not('http://' in jquery_url or 'https://' in jquery_url):
                    jquery_url= f'{url}{jquery_url}'
                response = requests.get(jquery_url)
                match = re.search(r'jQuery v(?P<version>\d+\.\d+(\.\d+)?)', response.text)
                if match:
                    jquery_version = match.groupdict().get('version')
                    if StrictVersion('1.2')< StrictVersion(jquery_version) < StrictVersion('3.5.0'):
                        error = "JQuery 1.2 < 3.5.0 Multiple XSS"
                        self.result += set_vul("CVE-2020-11022", error)
        except Exception as e:
            pass

    def jquery_detection_handler(self, target, regenerate):
        """
        This function detects the presence of JQuery on a remote host and generates a vulnerability
        report.
        
        :param target: The target parameter is an object that contains information about the target
        host, such as its IP address
        :param regenerate: The "regenerate" parameter is not used in the code snippet provided. It is
        not defined or referenced anywhere in the function
        """
        try:

            url = f'http://{target.ip}'
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            jquery_script = soup.find('script', src=lambda src: src and 'jquery' in src)
            if jquery_script:
                complexity = "INFO"
                error = "JQuery Detection"
                desc = 'System was able to detect JQuery on the remote host.'
                solution = "N/A"
                self.result+= set_info_vuln(
                    complexity=complexity,
                    error=error,
                    desc=desc,
                    solution=solution
                )

        except Exception as e:
            pass

    def asp_version_handler(self, target, regenerate):
        search_result = re.search(self.asp_version_regex, target.raw_result, re.IGNORECASE)
        if search_result:
            if search_result.groupdict().get('version'):
                asp_version = search_result.groupdict().get('version')
                if StrictVersion(asp_version) < StrictVersion('4.0'):
                    error = "X-AspNet-Version Response Header"
                    self.result += set_vul("CVE-2010-3332", error)

        
