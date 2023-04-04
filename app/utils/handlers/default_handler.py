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
        if regenerate or target.compose_result=="":
            self.result = f'''
                <div class="col-12 border border-1 border-dark">
                        <h2>{target.tool.tool_name.replace("-"," ").capitalize()}</h2>
                </div>
                <div class="col-12 border border-1 border-dark">
                    <div class="row">
                        <div class="col-3 border border-1 border-dark">
                            <h5>Other information</h5>
                        </div>
                        <div class="col-9 border border-1 border-dark">
                            <pre>
{escape(target.raw_result)}                           
                            </pre>
                        </div>
                    </div>
                </div>
                '''
            
        return self.result
        
        