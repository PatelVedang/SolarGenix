from bs4 import BeautifulSoup
import os
from scanner.models import *
from html import escape
import logging
logger = logging.getLogger('django')
import re
from .cve import CVE
cve = CVE()

class DEFAULT:
    port_search_regex = '(?P<port>\d{1,4}/tcp)\s+(?P<state>(filtered|open|closed))\s+(?P<service>[\w0-9\-\_]+).*(\n)'
    result = ""
    
    def default_handler(self, target, regenerate):
        """
        This function generates a default HTML response for a given target if target tool handler is not created.
        
        :param target: The target parameter is an object that contains information about the target
        being scanned, such as its URL and any vulnerabilities found during the scan
        :param regenerate: `regenerate` is a boolean parameter that indicates whether the result should
        be regenerated or not. If it is `True`, the result will be regenerated, otherwise, the existing
        result will be returned
        :return: the value of the variable `self.result`.
        """
        if regenerate or target.compose_result=="":
            complexity = "INFO"
            self.result =f'''
                <div class="row">
                    <div class="col-12 border border-5 border-light">
                        <div class="row vul-header">
                            <div class="col-3 border border-5 border-light {complexity}" data-id="complexity">
                                {complexity}
                            </div>
                            <div class="col-9 border border-5 border-light {complexity}" data-id="error">
                                {target.tool.tool_name.replace("-"," ").capitalize()}
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-3 border border-5 border-light body">
                                Other information
                            </div>
                            <div class="col-9 border border-5 border-light body">
                                <pre>
{escape(target.raw_result)}
                                </pre>
                            </div>
                        </div>
                    </div>
                </div>
                '''
            
        return self.result        
        