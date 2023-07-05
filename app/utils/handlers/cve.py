import requests
from bs4 import BeautifulSoup
import logging
logger = logging.getLogger('django')
import re
import json
from django.conf import settings
import aiohttp
import asyncio

class CVE:
    api_key = settings.NVD_API_KEY
    cve_details={}

    def update_cve(self, data):
        self.cve_details= {**self.cve_details, **data}
    
    def get_cve_details_by_id_v2(self, cve_id):
        """
        This function retrieves details of a CVE (Common Vulnerabilities and Exposures) using its ID
        from the NIST NVD (National Vulnerability Database) API 2.0 and updates the details in a dictionary.

        This function is use to get CVE details by NVD API.
        
        :param cve_id: The CVE ID (Common Vulnerabilities and Exposures) for which the details are being
        fetched
        :return: a dictionary containing details of a CVE (Common Vulnerabilities and Exposures)
        identified by the given CVE ID. The details include the CVE ID, description, CVSS (Common
        Vulnerability Scoring System) scores and error types for both version 2 and version 3, sources
        (references), and CWE (Common Weakness Enumeration) IDs.
        """
        self.cve_details={}
        url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "apiKey": self.api_key
        }
        params = {"cveId": cve_id}
        response = requests.get(url, headers=headers, params=params)
        self.set_cve_detail_v2(response)
        return self.cve_details
    
    def get_cve_details_by_id_v1(self, cve_id):
        """
        This function retrieves CVE details by ID from the NIST NVD API 1.0 and returns them as a
        dictionary.
        
        :param cve_id: The parameter `cve_id` is a string representing the Common Vulnerabilities and
        Exposures (CVE) identifier for a specific vulnerability. It is used to retrieve details about
        the vulnerability from the National Vulnerability Database (NVD) using the NVD REST API
        :return: a dictionary containing details of a CVE (Common Vulnerabilities and Exposures)
        identified by the given CVE ID. The details are obtained by making a REST API call to the NIST
        NVD (National Vulnerability Database) and parsing the JSON response.
        """
        self.cve_details={}
        url = f"https://services.nvd.nist.gov/rest/json/cve/1.0/{cve_id}"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "apiKey": self.api_key
        }
        response = requests.get(url, headers=headers)
        self.set_cve_detail_v1(response)
        return self.cve_details

    def set_cve_detail_v2(self, response):
        """
        This function sets the details of a Common Vulnerabilities and Exposures (CVE) entry based on a
        response from an API 2.0.
        
        :param response: The response object received from an API call
        """
        if response.status_code == 200:
            data = response.json()
            if data.get('vulnerabilities') and len(data.get('vulnerabilities')):
                if data['vulnerabilities'][0].get('cve'):
                    if data['vulnerabilities'][0]['cve'].get('descriptions'):
                        desc_index = next((index for (index, i) in enumerate(data['vulnerabilities'][0]['cve']['descriptions']) if i["lang"] == "en"), 0)
                        self.update_cve(
                            {
                                'cve_id':data['vulnerabilities'][0]['cve']['id'],
                                'description':data['vulnerabilities'][0]['cve']['descriptions'][desc_index]['value']
                            }
                        )
                    if data['vulnerabilities'][0]['cve'].get('metrics'):
                        if data['vulnerabilities'][0]['cve']['metrics'].get('cvssMetricV31'):
                            cvss3_index = next((index for (index, i) in enumerate(data['vulnerabilities'][0]['cve']['metrics']['cvssMetricV31']) if i["source"] == "nvd@nist.gov"), 0)
                            self.update_cve(
                                {
                                    'cvvs3':{
                                        'base_score': data['vulnerabilities'][0]['cve']['metrics']['cvssMetricV31'][cvss3_index]['cvssData']['baseScore'],
                                        'error_type': data['vulnerabilities'][0]['cve']['metrics']['cvssMetricV31'][cvss3_index]['cvssData']['baseSeverity'],
                                    }
                                }
                            )
                        else:
                            self.update_cve(
                                {
                                    'cvvs3':{
                                        'base_score': 'N/A',
                                        'error_type': 'N/A',
                                    }
                                }
                            )
                        if data['vulnerabilities'][0]['cve']['metrics'].get('cvssMetricV2'):
                            cvss2_index = next((index for (index, i) in enumerate(data['vulnerabilities'][0]['cve']['metrics']['cvssMetricV2']) if i["source"] == "nvd@nist.gov"), 0)
                            self.update_cve(
                                {
                                    'cvvs2':{
                                        'base_score': data['vulnerabilities'][0]['cve']['metrics']['cvssMetricV2'][cvss2_index]['cvssData']['baseScore'],
                                        'error_type': data['vulnerabilities'][0]['cve']['metrics']['cvssMetricV2'][cvss2_index]['cvssData']['accessComplexity'],
                                    }
                                }
                            )
                        else:
                            self.update_cve(
                                {
                                    'cvvs2':{
                                        'base_score': 'N/A',
                                        'error_type': 'N/A',
                                    }
                                }
                            )
                    if data['vulnerabilities'][0]['cve'].get('references'):
                        refences = [reference['url'] for reference in data['vulnerabilities'][0]['cve']['references']]
                        self.update_cve(
                            {
                            'sources': refences
                            }
                        )

                    if data['vulnerabilities'][0]['cve'].get('weaknesses'):
                        weaknesses = [cwe['value'] for weakness in data['vulnerabilities'][0]['cve']['weaknesses'] for cwe in weakness['description']]
                        self.update_cve(
                            {
                                'cwe_ids': weaknesses
                            }
                        )

                    if self.cve_details.get('cvvs3') and self.cve_details.get('cvvs3').get('error_type') and self.cve_details.get('cvvs3').get('error_type') != 'N/A':
                        complexity = self.cve_details['cvvs3'].get('error_type')
                    elif self.cve_details.get('cvvs2') and self.cve_details.get('cvvs2').get('error_type') and self.cve_details.get('cvvs2').get('error_type') != 'N/A':
                        complexity = self.cve_details['cvvs2'].get('error_type')
                    else:
                        complexity = "info"

                    self.update_cve(
                        {
                            'complexity': complexity
                        }
                    )
        
    def set_cve_detail_v1(self, response):
        """
        This function extracts various details of a CVE (Common Vulnerabilities and
        Exposures) from a JSON response of API 1.0.
        
        :param response: The response object received from an API call
        """
        if response.status_code == 200:
            data = response.json()
            cve_items = data.get('result').get('CVE_Items', [])
            if cve_items and len(cve_items):
                cve_item=cve_items[0]
                if cve_item.get('cve'):
                    cve_obj = cve_item.get('cve')
                    
                    description_obj = cve_obj.get('description',{})
                    if description_obj.get('description_data'):
                        desc_index = next((index for (index, i) in enumerate(cve_item.get('cve').get('description').get('description_data')) if i["lang"] == "en"), 0)
                        self.update_cve(
                                {
                                    'cve_id':cve_item.get('cve').get('CVE_data_meta').get('ID'),
                                    'description':cve_item.get('cve').get('description').get('description_data')[desc_index]['value']
                                }
                        )
                        
                    refences_obj = cve_obj.get('references',{})
                    if refences_obj.get('reference_data'):
                        refence_data_obj = refences_obj.get('reference_data')
                        refences = [reference['url'] for reference in refence_data_obj]
                        self.update_cve(
                            {
                                'sources': refences
                            }
                        )

                    problem_type_obj = cve_obj.get('problemtype',{})
                    if problem_type_obj.get('problemtype_data'):
                        problemtype_data_obj = problem_type_obj.get('problemtype_data')
                        weaknesses = [cwe['value'] for weakness in problemtype_data_obj for cwe in weakness['description']]
                        self.update_cve(
                                {
                                'cwe_ids': weaknesses
                                }
                        )

                cvvs3_obj = cve_item.get('impact',{}).get('baseMetricV3',{}).get('cvssV3',{})
                cvvs2_obj = cve_item.get('impact',{}).get('baseMetricV2',{}).get('cvssV2',{})
                self.update_cve(
                    {
                        'cvvs3':{
                                'base_score': cvvs3_obj.get('baseScore','N/A'),
                                'error_type': cvvs3_obj.get('baseSeverity','N/A'),
                        },
                        'cvvs2':{
                                'base_score': cvvs2_obj.get('baseScore','N/A'),
                                'error_type': cvvs2_obj.get('accessComplexity','N/A'),
                        }
                    }
                )

    def get_cve_details_by_keyword_v2(self, keyword):
        """
        This function retrieves CVE details from the NIST NVD API 2.0 based on a keyword search and returns
        the details in a dictionary format.
        
        :param keyword: The keyword parameter is a string that is used to search for Common
        Vulnerabilities and Exposures (CVE) details related to that keyword. The function uses the NIST
        National Vulnerability Database (NVD) API to retrieve the CVE details
        :return: a dictionary containing details of a Common Vulnerabilities and Exposures (CVE) entry
        that matches the given keyword. The details are obtained from the National Vulnerability
        Database (NVD) using the NVD REST API. The dictionary is populated with the CVE ID, description,
        published date, last modified date, and other relevant information.
        """
        self.cve_details={}
        url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "apiKey": self.api_key
        }
        params = {
            "keywordSearch": keyword,
            "resultsPerPage": 1
        }
        response = requests.get(url, headers=headers, params=params)
        self.set_cve_detail_v2(response)
        return self.cve_details

    def get_cve_details_by_keyword_v1(self, keyword):
        """
        This function retrieves CVE details from the NIST NVD API based on a given keyword with API 1.0.
        
        :param keyword: The keyword parameter is a string that is used to search for Common
        Vulnerabilities and Exposures (CVE) entries that contain the specified keyword in their
        description or summary
        :return: a dictionary containing details of a Common Vulnerabilities and Exposures (CVE) entry
        that matches the given keyword. The details are obtained from the National Vulnerability
        Database (NVD) using the NVD REST API.
        """
        self.cve_details={}
        url = f"https://services.nvd.nist.gov/rest/json/cves/1.0"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "apiKey": self.api_key
        }
        params = {
            "keyword": keyword,
            "resultsPerPage": 1,
        }
        response = requests.get(url, headers=headers, params=params)
        self.set_cve_detail_v1(response)
        return self.cve_details

    def set_cve_details_by_keyword_v2(self, keyword):
        """
        This function sets the CVE HTML details based on a keyword search API 2.0 of NVD.
        
        :param keyword: The keyword parameter is a string that is used to search for CVE (Common
        Vulnerabilities and Exposures) details. The function uses this keyword to retrieve the CVE
        details and then sets the HTML format of the details
        :return: the result of calling the method `set_cve_html` with the keyword arguments
        `**cve_details`.
        """
        cve_details = self.get_cve_details_by_keyword_v2(keyword)
        return self.set_cve_html(**cve_details)

    def set_cve_details_by_keyword_v1(self, keyword):
        """
        This function sets the CVE HTML details based on a keyword search API 1.0 of NVD.
        
        :param keyword: The keyword parameter is a string that is used to search for CVE (Common
        Vulnerabilities and Exposures) details. The function uses this keyword to retrieve CVE details
        and then sets the HTML content of the CVE details
        :return: the result of calling the method `set_cve_html` with the keyword arguments
        `**cve_details`.
        """
        cve_details = self.get_cve_details_by_keyword_v1(keyword)
        return self.set_cve_html(**cve_details)

    # This function will get cve by scraping cve from NVD template
    def get_cve_details_v1(self, cve):
        """
        It takes a CVE ID as an argument, and returns a dictionary containing the CVE ID, description,
        CVSS3 base score, CVSS3 error type, CVSS2 base score, and CVSS2 error type

        This function is use to get CVE details by scrapping NVD site.
        
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

    def set_cve_details_by_id_v2(self,cve):
        """
        This function sets the details of a CVE (Common Vulnerabilities and Exposures) and returns the
        corresponding HTML.
        
        :param cve: "cve" is a variable that represents a Common Vulnerabilities and Exposures (CVE)
        identifier, which is a unique identifier assigned to a specific security vulnerability. The
        function "set_cve_details_by_id" takes this identifier as input and retrieves the details of the
        vulnerability using the "get_cve_details
        :return: the result of calling the method `set_cve_html` with the keyword arguments unpacked
        from the dictionary `cve_details`.
        """
        cve_details = self.get_cve_details_by_id_v2(cve)
        return self.set_cve_html(**cve_details)
    
    def set_cve_details_by_id_v1(self,cve):
        """
        This function sets the details of a CVE (Common Vulnerabilities and Exposures) and returns the
        corresponding HTML.
        
        :param cve: "cve" is a variable that represents a Common Vulnerabilities and Exposures (CVE)
        identifier, which is a unique identifier assigned to a specific security vulnerability. The
        function "set_cve_details_by_id" takes this identifier as input and retrieves the details of the
        vulnerability using the "get_cve_details
        :return: the result of calling the method `set_cve_html` with the keyword arguments unpacked
        from the dictionary `cve_details`.
        """
        cve_details = self.get_cve_details_by_id_v1(cve)
        return self.set_cve_html(**cve_details)

    def get_complexity(self, cve):
        """
        This function retrieves the complexity of a CVE based on its details.
        
        :param cve: The parameter "cve" is a string representing the Common Vulnerabilities and
        Exposures (CVE) identifier for a specific security vulnerability
        :return: the complexity of a CVE (Common Vulnerabilities and Exposures) based on its details.
        The complexity can be "N/A" (not applicable), "Low", "Medium", "High", or "info".
        """
        cve_details = self.get_cve_details_by_id_v2(cve)
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
            
            if cve_details.get('location'):
                result += f'''
                <div class="row">
                    <div class="col-3 border border-5 border-light body">
                        Location
                    </div>
                    <div class="col-9 border border-5 border-light body">
                        {"<br>".join(cve_details['location'])}
                    </div>
                </div>
                '''

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
            
            if cve_details.get('cwe_ids'):
                result += f'''
                <div class="row">
                    <div class="col-3 border border-5 border-light body">
                        CWE ID
                    </div>
                    <div class="col-9 border border-5 border-light body">
                        {"<br>".join(cve_details['cwe_ids'])}
                    </div>
                </div>'''

            result += f'''
            <div class="row">
                <div class="col-3 border border-5 border-light body">
                    Solution
                </div>
                <div class="col-9 border border-5 border-light body">
                    {cve_details.get('solution') if (cve_details.get('solution') and cve_details.get('solution')!="N/A") else "Please visit the reference website for more information on how to patch this vulnerability."} 
                </div>
            </div>
            '''
            if cve_details.get('sources'):
                result += f'''
                <div class="row">
                    <div class="col-3 border border-5 border-light body">
                        References
                    </div>
                    <div class="col-9 border border-5 border-light body">
                        {"<br>".join(cve_details['sources'])}
                    </div>
                </div>
                '''
        return result

    
    async def mitre_keyword_search(self, keyword):
        """
        The function `mitre_keyword_search` performs a keyword search on the MITRE CVE database and
        returns the first CVE (Common Vulnerabilities and Exposures) ID found.
        
        :param keyword: The `keyword` parameter is a string that represents the keyword you want to
        search for in the MITRE CVE database
        :return: a CVE (Common Vulnerabilities and Exposures) identifier that matches the given keyword.
        If a matching CVE is found, it is returned as a string. If no matching CVE is found, an empty
        string is returned.
        """
        try:
            async with aiohttp.ClientSession() as session:
                url = f'https://cve.mitre.org/cgi-bin/cvekey.cgi?keyword={keyword.replace(" ","+")}'
                async with session.get(url) as response:
                    soup = BeautifulSoup(await response.text(), "html.parser")
                    vuln_table = soup.find("div", {'id': 'TableWithRules'})
                    if vuln_table:
                        rows = vuln_table.find_all('tr')
                        if rows and len(rows):
                            cols = rows[1].find_all('td')
                            if cols and len(cols):
                                cve = cols[0].find(string=True)
                                return cve
                        else:
                            return ""
                    else:
                        return ""
        except Exception as e:
            print(f"Keyword Search Error:{str(e)}")
            return ""
            
        


 