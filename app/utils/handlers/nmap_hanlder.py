from bs4 import BeautifulSoup
import os
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

class NMAP:
    port_search_regex = '(?P<port>\d{1,4}/(tcp|udp))\s+(?P<status>(filtered|open|closed|open\|filtered))\s+(?P<service>[\w0-9\-\_]+).*(\n)'
    ports = []
    open_ports_obj = {}

    def main(self, target, regenerate):
        """
        This is a Python function that handles different tool commands and their corresponding handlers
        to generate results for a given target.
        
        :param target: The target parameter is an object that represents the target to be scanned. It
        contains information such as the target's IP address, the tool to be used for scanning, and the
        raw result of the scan
        :param regenerate: A boolean flag that indicates whether the results for the target should be
        regenerated or not. If set to True, the code will regenerate the results for the target. If set
        to False, the code will return the previously generated results for the target
        :return: either the result of the executed tool command or the result of the default handler
        function, depending on whether the tool command is in the handlers dictionary or not.
        """
        handlers = {
            'nmap -Pn -sV -sT': [
                self.port_hanlder,
            ],
            'default': default.default_handler
        }
        tool_cmd = target.tool.tool_cmd.strip()
        if handlers.get(tool_cmd):
            if regenerate or target.compose_result=="":
                self.result = ""
                self.ports = []
                self.ports = list(re.finditer(self.port_search_regex, target.raw_result))
                for port_obj in self.ports:
                    if port_obj.groupdict().get('port'):
                        status = port_obj['status'].strip()
                        if status in ['open','filtered', 'open|filtered']:
                            port_number = port_obj['port'].split("/")[0]
                            service = port_obj['service']
                            self.open_ports_obj = {**self.open_ports_obj, **{port_number: {'port_with_protocol': port_obj.groupdict().get('port'), 'status':status, 'service': service}}}
                for vul_handler in handlers[tool_cmd]:
                    vul_handler(target, regenerate)
                Target.objects.filter(id=target.id).update(compose_result=self.result)
                return self.result
            else:
                self.result = target.compose_result
                return self.result
        else:
            return handlers['default'](target, regenerate)

    def port_hanlder(self, target, regenerate):
        """
        This function generates a set of information about a Cyber port scanner and its potential impact
        on a target network.
        
        :param target: The target parameter is the IP address or hostname of the system that is being
        scanned for open ports
        :param regenerate: The "regenerate" parameter is not used in the given code snippet. It is not
        defined as a parameter in the function signature and is not referenced within the function body
        :return: the result of the vulnerability scan as a string.
        """
        for port in self.open_ports_obj.keys():
            error = "Cyber PORT Scanner"
            port_number = self.open_ports_obj.get(port).get('port_with_protocol')
            status = self.open_ports_obj[port]['status']
            if status in ["open", "open|filtered"]: 
                complexity = "INFO"
                desc = "A Cyber port scanner is this plugin's function to find out open ports.Cyber port scanner are less intrusive than TCP (full connect) scans against broken services, but if the network is busy, they may cause issues for less capable firewalls and leave open connections on the remote target."
                solution = "Use an IP filter to shield your target."
            elif status in ["filtered"]:
                complexity = "FALSE-POSITIVE"
                desc = "A firewall, filter, or other network obstacle is blocking the port so that Cyber port scanner cannot tell whether it is open or closed."
                solution = "N/A"
            self.result+= set_info_vuln(
                complexity=complexity,
                error=error,
                desc=desc,
                solution=solution,
                port=port_number,
                tool="nmap"
            )
        return self.result

