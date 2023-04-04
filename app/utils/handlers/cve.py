import requests
from bs4 import BeautifulSoup
import logging
logger = logging.getLogger('django')
import re


class CVE:
    def get_cve_details(self, cve):
        """
        It takes a CVE ID as an argument, and returns a dictionary containing the CVE ID, description,
        CVSS3 base score, CVSS3 error type, CVSS2 base score, and CVSS2 error type
        
        :param cve: The CVE ID
        :return: A dictionary with the following keys:
            - cve_id
            - description
            - cvvs3
            - cvvs2
        """
        url = 'https://nvd.nist.gov/vuln/detail/' + cve
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        cve_details = {}
        cve_details['cve_id'] = cve
        cve_details['description'] = soup.find('p', {'data-testid': 'vuln-description'}).text if soup.find('p', {'data-testid': 'vuln-description'}) else 'N/A'
        cvv3 = soup.find('a', {'id': 'Cvss3NistCalculatorAnchor'}).text if soup.find('a', {'id': 'Cvss3NistCalculatorAnchor'}) else 'N/A'
        cvv2 = soup.find('a', {'id': 'Cvss2CalculatorAnchor'}).text if soup.find('a', {'id': 'Cvss2CalculatorAnchor'}) else 'N/A'
        cve_details = {**cve_details, **{
            'cvvs3': {
                'base_score': cvv3.split(" ")[0] if cvv3 and cvv3!='N/A' else 'N/A',
                'error_type': cvv3.split(" ")[1] if cvv3 and cvv3!='N/A' else 'N/A'
            },
            'cvvs2': {
                'base_score': cvv2.split(" ")[0] if cvv2 and cvv2!='N/A' else 'N/A',
                'error_type': cvv2.split(" ")[1] if cvv2 and cvv2!='N/A' else 'N/A'
            }
        }}
        if soup.findAll('td',{'data-testid':'vuln-CWEs-link-0'}):
            if soup.findAll('td',{'data-testid':'vuln-CWEs-link-0'})[0].find('a'):
                if soup.findAll('td',{'data-testid':'vuln-CWEs-link-0'})[0].find('a'):
                    cve_details = {**cve_details, **{'cwe_id': soup.findAll('td',{'data-testid':'vuln-CWEs-link-0'})[0].find('a').text.split("-")[1]}}
                    if soup.findAll('td',{'data-testid':'vuln-CWEs-link-0'})[1]:
                        cve_details = {**cve_details, **{'cwe_name': soup.findAll('td',{'data-testid':'vuln-CWEs-link-0'})[1].text}}
            if soup.find('div',{'id':'vulnHyperlinksPanel'}):
                cve_details['solution'] = re.sub('\s+',' ',soup.find('div',{'id':'vulnHyperlinksPanel'}).find('p').text).strip()

            sources = []
            if soup.find('table',{'data-testid':'vuln-hyperlinks-table'}):
                if soup.find('table',{'data-testid':'vuln-hyperlinks-table'}).findAll('tr'):
                    resource_rows = soup.find('table',{'data-testid':'vuln-hyperlinks-table'}).findAll('tr')
                    for row in resource_rows:
                        if row.find('a'):
                            sources.append(row.find('a')['href'])
                cve_details['sources'] = sources 
        logger.info(f'CVE details {cve_details}')
        return cve_details

    def set_cve_details(self,cve):
        result = ""
        cve_details = self.get_cve_details(cve)
        if cve_details:
            result = f'''
            <div class="row">
                <div class="col-3 border border-1 border-dark">
                    <h5>CVE ID</h5>
                </div>
                <div class="col-9 border border-1 border-dark d-flex">
                    {cve_details['cve_id']}
                </div>
            </div>'''
            if cve_details.get('cwe_name'):
                result += f'''
                <div class="row">
                    <div class="col-3 border border-1 border-dark">
                        <h5>Name</h5>
                    </div>
                    <div class="col-9 border border-1 border-dark">
                        {cve_details['cwe_name']}
                    </div>
                </div>'''

            result += f'''
            <div class="row">
                <div class="col-3 border border-1 border-dark">
                    <h5>Description</h5>
                </div>
                <div class="col-9 border border-1 border-dark d-flex justify-content-center">
                    {cve_details['description']}
                </div>
            </div>
            <div class="row">
                <div class="col-3 border border-1 border-dark">
                    <h5>CVVS 3 base score</h5>
                </div>
                <div class="col-9 border border-1 border-dark">
                    {cve_details['cvvs3']['base_score']}
                </div>
            </div>
            <div class="row">
                <div class="col-3 border border-1 border-dark">
                    <h5>CVVS 3 Complexity</h5>
                </div>
                <div class="col-9 border border-1 border-dark">
                    {cve_details['cvvs3']['error_type']}
                </div>
            </div>
            <div class="row">
                <div class="col-3 border border-1 border-dark">
                    <h5>CVVS 2 base score</h5>
                </div>
                <div class="col-9 border border-1 border-dark">
                    {cve_details['cvvs2']['base_score']}
                </div>
            </div>
            <div class="row">
                <div class="col-3 border border-1 border-dark">
                    <h5>CVVS 2 Complexity</h5>
                </div>
                <div class="col-9 border border-1 border-dark">
                    {cve_details['cvvs2']['error_type']}
                </div>
            </div>'''

            if cve_details.get('cwe_id'):
                result += f'''
                <div class="row">
                    <div class="col-3 border border-1 border-dark">
                        <h5>CWE ID</h5>
                    </div>
                    <div class="col-9 border border-1 border-dark">
                        {cve_details['cwe_id']}
                    </div>
                </div>'''

            result += f'''
            <div class="row">
                <div class="col-3 border border-1 border-dark">
                    <h5>Solution</h5>
                </div>
                <div class="col-9 border border-1 border-dark">
                    {cve_details['solution']}
                </div>
            </div>
            <div class="row">
                <div class="col-3 border border-1 border-dark">
                    <h5>Reference</h5>
                </div>
                <div class="col-9 border border-1 border-dark">
                    {"<br>".join(cve_details['sources'])}
                </div>
            </div>
            '''
        return result

 