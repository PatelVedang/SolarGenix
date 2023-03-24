import requests
from bs4 import BeautifulSoup
import logging
logger = logging.getLogger('django')



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
        cvv2 = soup.find('a', {'id': 'Cvss2CalculatorAnchor'}).text if soup.find('a', {'id': 'Cvss3NistCalculatorAnchor'}) else 'N/A'
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
                cve_details = {**cve_details, **{'cwe_id': soup.findAll('td',{'data-testid':'vuln-CWEs-link-0'})[0].find('a').text.split("-")[1]}}
            if soup.findAll('td',{'data-testid':'vuln-CWEs-link-0'})[1]:
                cve_details = {**cve_details, **{'cwe_name': soup.findAll('td',{'data-testid':'vuln-CWEs-link-0'})[1].text}}
        logger.info(f'CVE details {cve_details}')
        return cve_details

 