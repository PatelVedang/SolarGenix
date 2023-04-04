from bs4 import BeautifulSoup
import os
from scanner.models import *
from html import escape
import logging
logger = logging.getLogger('django')
import re
from .cve import CVE
cve = CVE()

class NMAP:
    port_search_regex = '(?P<port>\d{1,4}/tcp)\s+(?P<state>(filtered|open|closed))\s+(?P<service>[\w0-9\-\_]+).*(\n)'
    
    def nmap_handler(self, target, regenerate):
        """
        It takes a target and a boolean value as arguments, and returns a set_compose_result as the value
        
        :param target: The target to scan
        :param regenerate: If True, the scan will be re-run. If False, the scan will be loaded from the
        database
        :return: The result of the set_compose_result function.
        """
        return self.set_compose_result(target, regenerate)
    def nmap_poodle_handler(self, target, regenerate):
        return self.set_compose_result(target, regenerate)
    def nmap_vuln_handler(self, target, regenerate):
        return self.set_compose_result(target, regenerate)
    def nmap_vulners_handler(self, target, regenerate):
        return self.set_compose_result(target, regenerate)

    def set_compose_result(self, target, regenerate):
        """
        It takes the raw result of the tool and parses it to find the open ports and then it searches
        for the CVEs related to the open ports and then it formats the result and returns it
        
        :param target: The target object
        :param regenerate: If the result is already generated, then it will not be generated again
        :return: The result of the scan.
        """
        scan_result = target.raw_result
        ports = list(re.finditer(self.port_search_regex, scan_result))
        susceptible_ports = []
        result = ""
        if regenerate or target.compose_result=="":
            if ports:
                result = f'''
                    <div class="col-12 border border-1 border-dark">
                        <h2>{target.tool.tool_name.replace("-"," ").capitalize()}</h2>
                    </div>
                '''
                for index in range(len(ports)-1, -1, -1):
                    port_obj = ports[index].groupdict()
                    port = port_obj['port'].split("/")[0]
                    port_with_protocol = port_obj['port']
                    state = port_obj['state']
                    service = port_obj['service']
                    if state == "open":
                        result += f'''
                            <div class="col-12 border border-1 border-dark">
                                <h5>{port_with_protocol}({service})</h5>
                            </div>
                            <div class="col-12">
                                <div class="row">
                                    <div class="col-3 border border-1 border-dark">
                                        <h5>Port</h5>
                                    </div>
                                    <div class="col-9 border border-1 border-dark">
                                        {port}
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-3 border border-1 border-dark">
                                        <h5>Status</h5>
                                    </div>
                                    <div class="col-9 border border-1 border-dark">
                                        {state}
                                    </div>
                                </div>
                        '''
                        susceptible_ports.append(port)
                        value = scan_result.split(ports[index].group())[1]
                        if value.find('vulners') >= 0:
                            vulen = re.findall('CVE-\d{1,4}-\d{1,5}',value)
                            if vulen:
                                result += cve.set_cve_details(vulen[0])
                            formated_value = value.split("Service detection performed.")[0].replace("|_","").replace("|","").strip()
                            if formated_value:
                                result += f'''
                                                <div class="row">
                                                    <div class="col-3 border border-1 border-dark">
                                                        <h5>Other Information</h5>
                                                    </div>
                                                    <div class="col-9 border border-1 border-dark">
                                                        <blockquote>
                                                        <pre style="text-decoration:none;">
{escape(formated_value)}
                                                        </pre>
                                                        </blockquote>
                                                    </div>
                                                </div>
                                            '''
                            
                        result += '''
                            </div>
                        '''
                        scan_result = scan_result.split(ports[index].group())[0]
                        
            elif not susceptible_ports:
                result += f'''
                <div class="col-12 border border-1 border-dark">
                    <h2>{target.tool.tool_name.replace("-"," ").capitalize()}</h2>
                </div>
                <div class="col-12 border border-1 border-dark">
                    <h3>Not Found Any Vulnerability Threat Level</h3>
                </div>
                '''
            else:
                result += f'''
                <div class="col-12 border border-1 border-dark">
                    <h2>{target.tool.tool_name.replace("-"," ").capitalize()}</h2>
                </div>
                <div class="col-12 border border-1 border-dark">
                    <h3>Not Found Any Vulnerability Threat Level</h3>
                </div>
                '''
            Target.objects.filter(id=target.id).update(compose_result=result)
        else:
            result = target.compose_result
        return result


