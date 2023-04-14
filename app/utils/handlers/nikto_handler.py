from scanner.models import *
from html import escape
import logging
logger = logging.getLogger('django')
import re
from .cve import CVE
cve = CVE()
from .default_handler import DEFAULT
default = DEFAULT()
from .common_handler import set_vul

# The NIKTO class contains a method for handling the absence of an anti-clickjacking X-Frame-Options
# header in a target's raw result.
class NIKTO:
    anti_clickjacking_regex = "The anti-clickjacking X-Frame-Options header is not present."

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
            'nikto -host': self.anti_clickjacking_handler,
            'default': default.default_handler
        }
        tool_cmd = target.tool.tool_cmd.strip()
        if handlers.get(tool_cmd):
            return handlers[tool_cmd](target, regenerate)
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
        self.result = ""
        if regenerate or target.compose_result=="":
            if re.search(self.anti_clickjacking_regex, target.raw_result, re.IGNORECASE):
                error = "Missing Anti-clickjacking Header"
                self.result = set_vul("CVE-2018-17192", error)
            Target.objects.filter(id=target.id).update(compose_result=self.result)
        else:
            self.result = target.compose_result
        return self.result
