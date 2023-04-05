from scanner.models import *
from html import escape
import logging
logger = logging.getLogger('django')
import re
from .cve import CVE
cve = CVE()

class NIKTO:
    regex = "The anti-clickjacking X-Frame-Options header is not present."
    result = ""

    def nikto_handler(self, target, regenerate):
        if regenerate or target.compose_result=="":
            self.result = f'''
                <div class="col-12 border border-1 border-dark">
                        <h2>The anti-clickjacking X-Frame-Options header is not present.</h2>
                </div>'''
            
            if re.search(self.regex, target.raw_result, re.IGNORECASE):
                self.result +='''
                <div class="col-12">
                '''
                self.result += cve.set_cve_details('CVE-2018-17192')
                self.result +='''
                </div>
                '''
            else:
                self.result += f'''
                <div class="col-12 border border-1 border-dark">
                        <h3>Not Found Any Vulnerability Threat Level</h3>
                </div>'''
            Target.objects.filter(id=target.id).update(compose_result=self.result)
        else:
            self.result = target.compose_result
        return self.result
