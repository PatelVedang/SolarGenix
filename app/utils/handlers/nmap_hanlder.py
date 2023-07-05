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
    port_search_regex = '(?P<port>\d{1,5}/(tcp|udp))\s+(?P<status>(filtered|open|closed|open\|filtered))\s+(?P<service>[\w0-9\-\_\/]+)(?P<version>(\s*|.*))(\n)'
    cve_regex = "(cve|CVE)-[0-9]{4}-[0-9]{4,}"
    ports = []
    open_ports_obj = {}

    def replace_all_special_char(self, text):
        """
        The function replaces all special characters in a given text with their escaped versions.
        
        :param text: The `text` parameter is a string that contains the text in which you want to
        replace special characters
        :return: the modified text with all special characters replaced with their escaped versions.
        """
        return text.replace("\n","\\n").replace("\r","\\r").replace("\\n *", "\\n \*").replace(".", "\.").replace("^", "\^").replace("$", "\$").replace("*", "\*").replace("+", "\+").replace("?", "\?").replace("{", "\{").replace("}", "\}").replace("[", "\[").replace("]", "\]").replace("(", "\(").replace(")", "\)").replace("|", "\|").replace("{", "\{").replace("}", "\}")

    def remove_special_chars(self, text):
        """
        The function removes special characters from a given text.
        
        :param text: The "text" parameter is a string that contains the text from which you want to
        remove special characters
        :return: the modified text with special characters removed.
        """
        return text.replace("\n","").replace("\r","").replace("\\n *", "").replace("^", "").replace("$", "").replace("*", "").replace("+", "").replace("?", "").replace("{", "").replace("}", "").replace("[", "").replace("]", "").replace("(", "").replace(")", "").replace("|", "").replace("{", "").replace("}", "").strip()
    
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
                self.port_hanlder_v2
            ],
            # 'nmap -Pn -sV': [
            #     self.port_hanlder_v2
            # ],
            # 'nmap -Pn -sV --script=vulscan1/vulscan.nse': [
            #     self.port_hanlder,
            # ],
            'default': default.default_handler
        }
        tool_cmd = target.tool.tool_cmd.strip()
        if handlers.get(tool_cmd):
            if regenerate or not target.compose_result:
                self.result = {}
                self.ports = []
                self.ports = list(re.finditer(self.port_search_regex, target.raw_result))
                total_ports = len(self.ports)
                for port_index in range(total_ports):
                    if self.ports[port_index].groupdict().get('port'):
                        status = self.ports[port_index]['status'].strip()
                        if status in ['open','filtered', 'open|filtered']:
                            # if port_index==total_ports-1:
                            #     regex = f"""(?s){self.replace_all_special_char(self.ports[port_index].group())}(?P<content>.*?)$"""
                            # else:
                            #     regex = f"""(?s){self.replace_all_special_char(self.ports[port_index].group())}(?P<content>.*?){self.replace_all_special_char(self.ports[port_index+1].group())}"""
                            # cve_id = ""
                            # content_search_result = re.search(regex, target.raw_result)
                            # if content_search_result:
                            #     contect = content_search_result.groupdict()['content']
                            #     cve_search_result = re.finditer(self.cve_regex,contect)
                            #     cves = list(cve_search_result)
                            #     if cves:
                            #         cve_id = cves[0].group().strip()

                            port_number = self.ports[port_index]['port'].split("/")[0]
                            service = self.ports[port_index]['service']
                            version = self.remove_special_chars(self.ports[port_index]['version'])
                            # self.open_ports_obj = {**self.open_ports_obj, **{port_number: {'port_with_protocol': self.ports[port_index].groupdict().get('port'), 'status':status, 'service': service, 'cve': cve_id}}}
                            self.open_ports_obj = {**self.open_ports_obj, **{port_number: {'port_with_protocol': self.ports[port_index].groupdict().get('port'), 'status':status, 'service': service, 'version': version}}}
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
            port_number = self.open_ports_obj.get(port).get('port_with_protocol')
            error = f"Cyber PORT Scanner {port_number}"
            evidence = f"{self.open_ports_obj[port]['port_with_protocol']} {self.open_ports_obj[port]['status']} {self.open_ports_obj[port]['service']}"
            status = self.open_ports_obj[port]['status']
            if status in ["open", "open|filtered"]: 
                complexity = "INFO"
                desc = "A Cyber port scanner is this plugin's function to find out open ports.Cyber port scanner are less intrusive than TCP (full connect) scans against broken services, but if the network is busy, they may cause issues for less capable firewalls and leave open connections on the remote target."
                solution = "Use an IP filter to shield your target."
            elif status in ["filtered"]:
                complexity = "FALSE-POSITIVE"
                desc = "A firewall, filter, or other network obstacle is blocking the port so that Cyber port scanner cannot tell whether it is open or closed."
                solution = "N/A"
            self.result = {**self.result, **alert_response(
                complexity=complexity,
                error=error,
                description=desc,
                solution=solution,
                port=port_number,
                tool="nmap",
                alert_type=4,
                evidence=evidence
            )}
    

    async def set_vul_data(self, port):
        """
        The function `set_vul_data` sets vulnerability data based on the given port number.
        
        :param port: The `port` parameter is the port number for which you want to set vulnerability
        data
        """
        port_number = self.open_ports_obj.get(port).get('port_with_protocol')
        error = f"Cyber PORT Scanner {port_number}"
        evidence = f"{self.open_ports_obj[port]['port_with_protocol']} {self.open_ports_obj[port]['status']} {self.open_ports_obj[port]['service']}"
        version = self.open_ports_obj.get(port).get('version')
        if version:
            cve_id = await cve.mitre_keyword_search(version)
            self.result = {**self.result, **alert_response(cve=cve_id, error=error, tool="nmap", alert_type=1, evidence=evidence)}
        else:
            status = self.open_ports_obj[port]['status']
            if status in ["open", "open|filtered"]: 
                complexity = "INFO"
                desc = "A Cyber port scanner is this plugin's function to find out open ports.Cyber port scanner are less intrusive than TCP (full connect) scans against broken services, but if the network is busy, they may cause issues for less capable firewalls and leave open connections on the remote target."
                solution = "Use an IP filter to shield your target."
            elif status in ["filtered"]:
                complexity = "FALSE-POSITIVE"
                desc = "A firewall, filter, or other network obstacle is blocking the port so that Cyber port scanner cannot tell whether it is open or closed."
                solution = "N/A"
            self.result = {**self.result, **alert_response(
                complexity=complexity,
                error=error,
                description=desc,
                solution=solution,
                port=port_number,
                tool="nmap",
                alert_type=4,
                evidence=evidence
            )}


    def port_hanlder_v2(self, target, regenerate):
        """
        The function `port_handler_v2` is an asynchronous function that iterates over a list of open
        ports and sets vulnerability data for each port.
        
        :param target: The "target" parameter is the IP address or hostname of the target system that
        you want to perform port handling on
        :param regenerate: The `regenerate` parameter is a boolean value that determines whether the
        vulnerability data should be regenerated or not. If `regenerate` is `True`, the vulnerability
        data will be regenerated. If `regenerate` is `False`, the existing vulnerability data will be
        used
        """
        async def sub():
            """
            The function `sub` creates a list of jobs to set vulnerability data for each open port and
            uses `asyncio.gather` to execute them concurrently.
            """
            jobs = []
            for port in self.open_ports_obj.keys():
                jobs.append(self.set_vul_data(port))
            await asyncio.gather(*jobs)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(sub())
        loop.close()