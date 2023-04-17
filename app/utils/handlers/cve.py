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
        """
        This function sets the details of a CVE (Common Vulnerabilities and Exposures) and returns the
        corresponding HTML.
        
        :param cve: "cve" is a variable that represents a Common Vulnerabilities and Exposures (CVE)
        identifier, which is a unique identifier assigned to a specific security vulnerability. The
        function "set_cve_details" takes this identifier as input and retrieves the details of the
        vulnerability using the "get_cve_details
        :return: the result of calling the method `set_cve_html` with the keyword arguments unpacked
        from the dictionary `cve_details`.
        """
        cve_details = self.get_cve_details(cve)
        return self.set_cve_html(**cve_details)

    def get_complexity(self, cve):
        """
        This function retrieves the complexity of a CVE based on its details.
        
        :param cve: The parameter "cve" is a string representing the Common Vulnerabilities and
        Exposures (CVE) identifier for a specific security vulnerability
        :return: the complexity of a CVE (Common Vulnerabilities and Exposures) based on its details.
        The complexity can be "N/A" (not applicable), "Low", "Medium", "High", or "info".
        """
        cve_details = self.get_cve_details(cve)
        if cve_details['cvvs3'].get('error_type') and cve_details['cvvs3'].get('error_type') != 'N/A':
            complexity = cve_details['cvvs3'].get('error_type')
        elif cve_details['cvvs2'].get('error_type') and cve_details['cvvs2'].get('error_type') != 'N/A':
            complexity = cve_details['cvvs2'].get('error_type')
        else:
            complexity = "info"

        return complexity
    
    def set_cve_html(self, **cve_details):
        """
        This function sets the HTML format for displaying details of a CVE (Common Vulnerabilities and
        Exposures) and returns the HTML code along with the complexity level of the CVE.
        :return: a tuple containing two values: a string variable named "result" and a string variable
        named "complexity".
        """
        result = ""
        if cve_details:
            if cve_details.get('cve_id'):
                result += f'''
                <div class="row">
                    <div class="col-3 border border-5 border-light body">
                        CVE ID
                    </div>
                    <div class="col-9 border border-5 border-light body">
                        {cve_details['cve_id']}
                    </div>
                </div>'''
            
            if cve_details.get('description'):
                result += f'''
                <div class="row">
                    <div class="col-3 border border-5 border-light body">
                        Description
                    </div>
                    <div class="col-9 border border-5 border-light body">
                        {cve_details['description']}
                    </div>
                </div>
                '''
            
            if cve_details.get('cvvs3'):
                if cve_details['cvvs3'].get('base_score'):
                    result += f'''
                    <div class="row">
                        <div class="col-3 border border-5 border-light body">
                            CVVS 3 base score
                        </div>
                        <div class="col-9 border border-5 border-light body">
                            {cve_details['cvvs3']['base_score']}
                        </div>
                    </div>
                    '''
                if cve_details['cvvs3'].get('error_type'):
                    result += f'''
                    <div class="row">
                        <div class="col-3 border border-5 border-light body">
                            CVVS 3 Complexity
                        </div>
                        <div class="col-9 border border-5 border-light body">
                            {cve_details['cvvs3']['error_type']}
                        </div>
                    </div>'''

            if cve_details.get('cvvs2'):
                if cve_details['cvvs2'].get('base_score'):
                    result += f'''
                    <div class="row">
                        <div class="col-3 border border-5 border-light body">
                            CVVS 2 base score
                        </div>
                        <div class="col-9 border border-5 border-light body">
                            {cve_details['cvvs2']['base_score']}
                        </div>
                    </div>
                    '''
                if cve_details['cvvs2'].get('error_type'):
                    result += f'''
                    <div class="row">
                        <div class="col-3 border border-5 border-light body">
                            CVVS 2 Complexity
                        </div>
                        <div class="col-9 border border-5 border-light body">
                            {cve_details['cvvs2']['error_type']}
                        </div>
                    </div>'''
            
            if cve_details.get('cwe_id'):
                result += f'''
                <div class="row">
                    <div class="col-3 border border-5 border-light body">
                        CWE ID
                    </div>
                    <div class="col-9 border border-5 border-light body">
                        {cve_details['cwe_id']}
                    </div>
                </div>'''

            if cve_details.get('solution'):
                result += f'''
                <div class="row">
                    <div class="col-3 border border-5 border-light body">
                        Solution
                    </div>
                    <div class="col-9 border border-5 border-light body">
                        {cve_details['solution']}
                    </div>
                </div>
                '''
            if cve_details.get('sources'):
                result += f'''
                <div class="row">
                    <div class="col-3 border border-5 border-light body">
                        Reference
                    </div>
                    <div class="col-9 border border-5 border-light body">
                        {"<br>".join(cve_details['sources'])}
                    </div>
                </div>
                '''
        if cve_details['cvvs3'].get('error_type') and cve_details['cvvs3'].get('error_type') != 'N/A':
            complexity = cve_details['cvvs3'].get('error_type')
        elif cve_details['cvvs2'].get('error_type') and cve_details['cvvs2'].get('error_type') != 'N/A':
            complexity = cve_details['cvvs2'].get('error_type')
        else:
            complexity = "info"
        
        return result, complexity
            
        


 