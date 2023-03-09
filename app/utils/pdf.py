from django.conf import settings
import pdfkit
import re
import uuid
from scanner.models import Target
import os
from bs4 import BeautifulSoup
import requests
from html import escape

class PDF:
    PDF_PATH = f'{settings.MEDIA_ROOT}pdf'
    result = ""

    def make_path(self, target_path):
        """
        It takes a path, splits it into a list, and then iterates over the list, creating a directory
        for each item in the list
        
        :param target_path: The path to the directory you want to create
        """
        sub_path = target_path.replace(str(settings.BASE_DIR), '')
        sub_path_content = sub_path.split("/")
        for index in range(len(sub_path_content)):
            path = f'{settings.BASE_DIR}{"/".join(sub_path_content[:index+1])}'
            if not os.path.exists(path):
                os.mkdir(path)
            self.path = path

    def generate(self, user_id, target_id, generate_pdf=True):
        """
        It takes a string of text, finds all the ports in it, and then returns a string of HTML that
        contains a table of the ports and their vulnerabilities
        
        :param user_id: The user id of the user who is requesting the report
        :param target_id: The id of the target you want to generate a report for
        :param generate_pdf: If you want to generate a pdf file, set it to True, defaults to True
        (optional)
        """
        port_search_regex = '(?P<port>\d{1,4}/tcp)\s+(?P<state>(filtered|open|closed)).*(\n)'
        target_obj = Target.objects.get(id=target_id)
        self.scan_result = target_obj.result
        # scan_result_copy = target_obj.result
        self.ports = list(re.finditer(port_search_regex, self.scan_result))
        self.result = ""
        self.susceptible_ports = []
        
        if self.ports:
            self.set_result()

        if not self.susceptible_ports:
            self.result = '''
            <div class="col-12 border border-1 border-dark">
                <h2>Not Found Any Vulnerability Threat Level</h2>
            </div>
            '''

        html_data = f"""<!DOCTYPE html>
        <html lang="en">
        <head>
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.6.2/dist/css/bootstrap.min.css"
                integrity="sha384-xOolHFLEh07PJGoPkLv1IbcEPTNtaed2xpHsD9ESMhqIYd0nLMwNLD69Npy4HI+N" crossorigin="anonymous">
        </head>

        <body>
            <div class="container-fluid">   
                <div class="row border border-1 border-dark">
                    {self.result}
                </div>
            </div>
        </body>

        </html>"""

        if generate_pdf:
            self.make_path(f'{self.PDF_PATH}/{user_id}/{target_id}')
                
            if target_obj.pdf_path:
                if os.path.exists(f'{settings.MEDIA_ROOT}/{target_obj.pdf_path}'):
                    os.remove(f'{settings.MEDIA_ROOT}/{target_obj.pdf_path}')

            new_pdf_name = f'{str(uuid.uuid4())}.pdf'
            file_path = f'{self.path}/{new_pdf_name}'
            options={
            '--page-size': 'A4',
            'margin-top': '0.5in',
            'margin-right': '0.5in',
            'margin-bottom': '0.5in',
            'margin-left': '0.5in'
            }
            pdfkit.from_string(html_data, output_path=file_path, options=options)
            file_path_for_db = file_path.replace(str(settings.MEDIA_ROOT), '')
            Target.objects.filter(id=target_id).update(pdf_path=file_path_for_db)
            file_url = f"{settings.PDF_DOWNLOAD_ORIGIN}/media/{file_path_for_db}"
            return file_path, new_pdf_name, file_url
        else:
            return html_data.replace("\n","")
        
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
        return cve_details

    
    def set_result(self):
        """
        It takes the output of the nmap scan and parses it to extract the information about the open
        ports and the vulnerabilities associated with them
        """
        for index in range(len(self.ports)-1, -1, -1):
            port_obj = self.ports[index].groupdict()
            port = port_obj['port'].split("/")[0]
            port_with_protocol = port_obj['port']
            state = port_obj['state']
            if state == "open":
                self.result += f'''
                    <div class="col-12 border border-1 border-dark">
                        <h2>{port_with_protocol}</h2>
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
                self.susceptible_ports.append(port)
                value = self.scan_result.split(self.ports[index].group())[1]
                if value.find('vulners') >= 0:
                    vulen = re.findall('CVE-\d{1,4}-\d{1,5}',value)
                    print("****",vulen[0].strip(" "),"****")
                    if vulen:
                        cve_details = self.get_cve_details(vulen[0])
                        if cve_details:
                            self.result += f'''
                                <div class="row">
                                    <div class="col-3 border border-1 border-dark">
                                        <h5>CVE ID</h5>
                                    </div>
                                    <div class="col-9 border border-1 border-dark d-flex">
                                        {cve_details['cve_id']}
                                    </div>
                                </div>
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
                                </div>
                            '''
                formated_value = value.split("Service detection performed.")[0].replace("|_","").replace("|","").strip()
                print(formated_value)
                if formated_value:
                    self.result += f'''
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
                
                self.result += '''
                    </div>
                '''
            self.scan_result = self.scan_result.split(self.ports[index].group())[0]
