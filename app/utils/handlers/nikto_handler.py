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
            self.result = ""
            if re.search(self.regex, target.raw_result, re.IGNORECASE):
                self.result ='''
                <div class="col-12 border border-1 border-dark" style="background-color:orange;">
                        <h2 style="color:white;">Missing Anti-clickjacking Header.</h2>
                </div>
                <div class="col-12">
                '''
                self.result += cve.set_cve_details('CVE-2018-17192')
                self.result +='''
                </div>
                '''
            else:
                self.result = f'''
                <div class="col-12 border border-1 border-dark">
                        <h2>Nikto.</h2>
                </div>
                <div class="col-12 border border-1 border-dark">
                        <h3>No Vulnerability Threat Level Found</h3>
                </div>'''
            Target.objects.filter(id=target.id).update(compose_result=self.result)
        else:
            self.result = target.compose_result
        return self.result
