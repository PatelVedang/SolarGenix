from scanner.models import *
from html import escape
import logging
logger = logging.getLogger('django')
import re
import requests
from distutils.version import StrictVersion
from bs4 import BeautifulSoup
from .cve import CVE
cve = CVE()
from .default_handler import DEFAULT
default = DEFAULT()
from .common_handler import *
from tldextract import extract

# The NIKTO class contains a method for handling the absence of an anti-clickjacking X-Frame-Options
# header in a target's raw result.
class NIKTO:
    anti_clickjacking_regex = "The anti-clickjacking X-Frame-Options header is not present."
    asp_version_regex = "Retrieved x-aspnet-version header: (?P<version>\d+\.\d+(\.\d+)?)"
    cookie_regex = "Cookie\s+(?P<cname>(\w)+)\s+created without the httponly flag"
    update_method_regex = "PUT method allowed"
    delete_method_regex = "DELETE method enabled"
    XSS_regex = "vulnerable\s+to\s+Cross+\s+Site+\s+Scripting\s+\(XSS\)"
    subdomain_regex = "Subdomain\s+(?P<subdomain>\w+)\s+found"
    cgi_regex = "\+\s+CGI directories"
    outdated_regex = "outdated"
    shellshock_regex = "(\s*|\')shellshock(\s*|\')\s+vulnerability.+(?P<cve>(cve|CVE)-[0-9]{4}-[0-9]{4,})[^\\n]+\\n"
    httpoptions_regex = "Allowed HTTP Methods"
    sitefiles_regex= "\s+/(?P<file>[/\w\.]*):[\s\w]+file found(\\n|\\r\\n)"


    def main(self, target, regenerate):
        """
        This function selects a handler based on the tool command and executes it with the given target
        and regenerate parameters.
        
        :param target: The "target" parameter is an object that contains information about the target
        being scanned, such as its URL, IP address, and other relevant details. It is passed as an
        argument to the main function
        :param regenerate: The `regenerate` parameter is a boolean value that indicates whether or not
        to regenerate the output of the tool being used. If `regenerate` is `True`, the output will be
        regenerated, otherwise the existing output will be used
        :return: the result of calling one of two possible handlers, depending on the value of
        `tool_cmd`. If `tool_cmd` is equal to `'nikto -host'`, it will call the
        `anti_clickjacking_handler` function with the `target` and `regenerate` arguments. Otherwise, it
        will call the `default_handler` function with the same arguments. The result
        """
        handlers = {
            'nikto -host': [
                self.anti_clickjacking_handler,
                self.jquery_handler,
                self.jquery_detection_handler,
                self.asp_version_handler,
                self.cookie_hanlder,
                self.put_del_handler,
                self.XSS_handler,
                self.subdomain_handler,
                self.cgi_dir_handler,
                self.resource_outdated_handler,
                self.shellshock_handler,
                self.httpoptions_handler,
                self.sitefiles_handler
            ],
            'nikto -Format htm -output - -h': [self.nikto_built_in_report_handler],
            'default': default.default_handler
        }
        tool_cmd = target.tool.tool_cmd.strip()
        if handlers.get(tool_cmd):
            regenerate=True
            if regenerate or target.compose_result=="":
                self.result = ""
                for vul_handler in handlers[tool_cmd]:
                    vul_handler(target, regenerate)
                Target.objects.filter(id=target.id).update(compose_result=self.result)
                return self.result
            else:
                self.result = target.compose_result
                return self.result
        else:
            return handlers['default'](target, regenerate)

    def anti_clickjacking_handler(self, target, regenerate):
        """
        This function checks for the presence of an anti-clickjacking header and sets a vulnerability if
        it is missing.
        
        :param target: The `target` parameter is an object that represents the target website or web
        application that is being scanned for vulnerabilities. It likely contains information such as
        the URL, HTTP headers, and response data
        :param regenerate: A boolean parameter that indicates whether the result should be regenerated
        or not. If set to True, the function will regenerate the result even if it already exists. If
        set to False, the function will return the existing result without regenerating it
        :return: the value of the "result" variable, which is either an empty string or a string
        containing a vulnerability message.
        """
        
        if re.search(self.anti_clickjacking_regex, target.raw_result, re.IGNORECASE):
            error = "Missing Anti-clickjacking Header"
            self.result += set_vul("CVE-2018-17192", error, "nikto")
    
    def jquery_handler(self, target, regenerate):
        """
        This function checks if a website is using a vulnerable version of jQuery and reports it as a
        potential XSS vulnerability.
        
        :param target: The target parameter is an object that contains information about the target
        website, including its IP address
        :param regenerate: The "regenerate" parameter is not used in the given code snippet. It is not
        clear what its purpose is without further context
        """
        try:
            url = f'http://{target.ip}'
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            jquery_script = soup.find('script', src=lambda src: src and 'jquery' in src)

            if jquery_script:
                jquery_url = jquery_script['src']
                if not('http://' in jquery_url or 'https://' in jquery_url):
                    jquery_url= f'{url}{jquery_url}'
                response = requests.get(jquery_url)
                match = re.search(r'jQuery v(?P<version>\d+\.\d+(\.\d+)?)', response.text)
                if match:
                    jquery_version = match.groupdict().get('version')
                    if StrictVersion('1.2')< StrictVersion(jquery_version) < StrictVersion('3.5.0'):
                        error = "JQuery 1.2 < 3.5.0 Multiple XSS"
                        self.result += set_vul("CVE-2020-11022", error, "nikto")
        except Exception as e:
            pass

    def jquery_detection_handler(self, target, regenerate):
        """
        This function detects the presence of JQuery on a remote host and generates a vulnerability
        report.
        
        :param target: The target parameter is an object that contains information about the target
        host, such as its IP address
        :param regenerate: The "regenerate" parameter is not used in the code snippet provided. It is
        not defined or referenced anywhere in the function
        """
        try:

            url = f'http://{target.ip}'
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            jquery_script = soup.find('script', src=lambda src: src and 'jquery' in src)
            if jquery_script:
                complexity = "INFO"
                error = "JQuery Detection"
                desc = 'System was able to detect JQuery on the remote host.'
                solution = "N/A"
                self.result+= set_info_vuln(
                    complexity=complexity,
                    error=error,
                    desc=desc,
                    solution=solution,
                    tool="nikto"
                )

        except Exception as e:
            pass

    def asp_version_handler(self, target, regenerate):
        """
        The function checks the version of ASP.NET in a response header and sets a vulnerability if it
        is less than version 4.0.
        
        :param target: The target parameter is an object that contains information about the target
        system, such as the URL, headers, and response data. It is used in this function to extract the
        X-AspNet-Version response header from the target's raw_result attribute
        :param regenerate: The `regenerate` parameter is a boolean value that indicates whether the
        target should be regenerated or not. It is not used in the code snippet provided
        """
        search_result = re.search(self.asp_version_regex, target.raw_result, re.IGNORECASE)
        if search_result:
            if search_result.groupdict().get('version'):
                asp_version = search_result.groupdict().get('version')
                if StrictVersion(asp_version) < StrictVersion('4.0'):
                    error = "X-AspNet-Version Response Header"
                    self.result += set_vul("CVE-2010-3332", error, "nikto")

    def cookie_hanlder(self, target, regenerate):
        """
        This function checks if a target has a sensitive cookie without the 'HttpOnly' flag and adds a
        vulnerability to the result if it does.
        
        :param target: The target parameter is a variable that contains the result of a HTTP request
        made to a web application. It is used to check if the response contains a sensitive cookie
        without the 'HttpOnly' flag
        :param regenerate: The "regenerate" parameter is not used in the given code snippet. It is not
        defined or referenced anywhere in the function
        """
        if re.search(self.cookie_regex, target.raw_result, re.IGNORECASE):
            error = "Sensitive Cookie Without 'HttpOnly' Flag"
            self.result += set_vul("CVE-2021-27764", error, "nikto")

    def put_del_handler(self, target, regenerate):
        """
        This function checks if insecure HTTP PUT and DELETE methods are allowed in a web server and
        sets a vulnerability if found.
        
        :param target: The target parameter is an object that represents the web server being scanned
        for vulnerabilities. It likely contains information such as the server's IP address, port
        number, and other relevant details
        :param regenerate: The `regenerate` parameter is not used in the `put_del_handler` method. It is
        not defined in the method signature and is not referenced within the method body
        """
        if re.search(self.update_method_regex, target.raw_result, re.IGNORECASE) and re.search(self.update_method_regex, target.raw_result, re.IGNORECASE):
            error = "Insecurely HTTP PUT and DELETE methods are allowed in web server"
            self.result += set_vul("CVE-2021-35243", error, "nikto")

    def XSS_handler(self, target, regenerate):
        """
        This function checks if a target contains a cross-site scripting vulnerability and sets a CVE
        identifier and error message if it does.
        
        :param target: The target parameter is likely an object or variable that contains the result of
        a web request or response. The code is checking if the raw result of the target object matches a
        regular expression for cross-site scripting (XSS) vulnerabilities
        :param regenerate: The "regenerate" parameter is not used in the given code snippet. It is not
        defined or referenced anywhere in the function
        """
        if re.search(self.XSS_regex, target.raw_result, re.IGNORECASE):
            error = "A cross-site scripting (XSS) in JavaScript or HTML"
            self.result += set_vul("CVE-2022-39195", error, "nikto")

    def subdomain_handler(self, target, regenerate):
        """
        This function checks for a possible subdomain leak in the target and sets a vulnerability if
        found.
        
        :param target: The target parameter is an object that contains information about the target
        being scanned, such as its URL, response headers, and response body. It is used in this function
        to check if the response body contains a potential subdomain leak
        :param regenerate: The "regenerate" parameter is not used in the given code snippet. It is not
        defined or referenced anywhere in the function
        """
        if re.search(self.subdomain_regex, target.raw_result, re.IGNORECASE):
            root_domain = ".".join(list(extract(target.ip)[1:])).strip()
            subdomains = [f"{subdomain.groupdict().get('subdomain')}.{root_domain}" for subdomain in re.finditer(self.subdomain_regex, target.raw_result)]
            error = "Possible subdomain leak"
            data = cve.get_cve_details_by_id_v2("CVE-2018-7844")
            self.result += set_custom_vul(**{**data, **{'location':subdomains, 'error': error, 'tool': 'nikto'}})

    def cgi_dir_handler(self, target, regenerate):
        """
        This function checks if a target matches a regular expression for CGI scripts and adds a
        vulnerability to the result if it does.
        
        :param target: The target parameter is an object that represents the HTTP response received from
        the server. It contains information such as the response headers, status code, and response body
        :param regenerate: The "regenerate" parameter is not used in the code snippet provided. It is
        not defined or referenced anywhere in the function
        """
        if re.search(self.cgi_regex, target.raw_result, re.IGNORECASE):
            error = "HTTP Methods Allowed (per directory)"
            self.result += set_vul("CVE-2022-27615", error, "nikto")
    
    def resource_outdated_handler(self, target, regenerate):
        """
        This function checks if a target's raw result contains outdated resources and sets a
        vulnerability if it does.
        
        :param target: The target parameter is an object that represents the resource being checked for
        outdatedness. It likely contains information such as the URL or file path of the resource, as
        well as any relevant metadata or headers
        :param regenerate: The `regenerate` parameter is not used in the given code snippet. It is not
        defined or referenced anywhere in the function
        """
        if re.search(self.outdated_regex, target.raw_result, re.IGNORECASE):
            error = "Outdated resources found"
            self.result += set_vul("CVE-2022-27615", error, "nikto")

    def shellshock_handler(self, target, regenerate):
        """
        This function checks if a server is vulnerable to the Shellshock exploit and sets the
        vulnerability accordingly.
        
        :param target: The target parameter is an object that represents the target server or
        application being tested for vulnerabilities. It likely contains information such as the
        target's IP address, port number, and other relevant details
        :param regenerate: It is a boolean parameter that determines whether the target should be
        regenerated or not. It is not used in the given code snippet
        """
        if re.search(self.shellshock_regex, target.raw_result, re.IGNORECASE):
            if re.search(self.shellshock_regex, target.raw_result, re.IGNORECASE).groupdict().get('cve'):
                cve = re.search(self.shellshock_regex, target.raw_result, re.IGNORECASE).groupdict().get('cve')
                error = "shellshock present in server"
                self.result += set_vul(cve, error, "nikto")

    def httpoptions_handler(self, target, regenerate):
        """
        This function checks for insecure HTTP methods in Apache and sets a vulnerability if found.
        
        :param target: The target is an object that contains information about the target system, such
        as its IP address, port number, and protocol. In this case, it also contains the raw result of a
        previous scan
        :param regenerate: The "regenerate" parameter is not used in the code snippet provided. It is
        not defined or referenced anywhere in the function
        """
        if re.search(self.httpoptions_regex, target.raw_result, re.IGNORECASE):
            error = "Insecure HTTP methods in Apache"
            self.result += set_vul("CVE-2017-7685", error, "nikto")

    def sitefiles_handler(self, target, regenerate):
        """
        This function checks for site files disclosure and generates a custom vulnerability report if
        found.
        
        :param target: The target is an object that contains information about the website or
        application being scanned, such as its URL, response headers, and response body
        :param regenerate: The "regenerate" parameter is not used in the given code snippet. It is not
        defined or referenced anywhere in the function
        """
        if re.search(self.sitefiles_regex, target.raw_result, re.IGNORECASE):
            files = [file.groupdict().get('file') for file in re.finditer(self.sitefiles_regex, target.raw_result)]
            error = "Site files disclosure"
            data = {
                'cve_id': 'N/A',
                'description': 'These are files that are accessible from the web site.',
                'location':files,
                'cvvs3': {
                'base_score': '10',
                'error_type': 'CRITICAL'
                },
                'cwe_ids': ['CWE-200'],
                'cwe_name': 'N/A',
                'solution': "Remove any sensitive information that may have been left behind. If it's not possible to remove it, block access to it from the HTTP server.",
                'sources': [
                'N/A'
                ],
                'error': error,
                'tool': 'nikto'
            }
            self.result += set_custom_vul(**data)

    
    def nikto_built_in_report_handler(self, target, regenerate):
        soup = BeautifulSoup(target.raw_result, "html.parser")
        tables = soup.find_all('table',{'class':'dataTable'})
        result = {}
        for index in range(len(tables)):
            table_obj = {}
            rows = tables[index].find_all('tr')
            for row in rows:
                columns = row.find_all('td')
                if len(columns) == 2:
                    table_obj= {**table_obj, **{columns[0].find(string=True):columns[1].find(string=True, href=True) if columns[1].find(string=True, href=True) else columns[1].find(string=True)}}

            result= {**result, **{index:table_obj}}
        if result:
            # cve.set_cve_html
            for key, val in result.items():
                # ####################
                #   content start which update in future
                # ####################
                if list(result.keys()).index(key) in [0,1,2] or True:
                    if val.get('Description'):
                        error = val.get('Description').replace("/:","")
                        # data = {
                        #     'cve_id': 'N/A',
                        #     'description': val.get('Description'),
                        #     'cvvs3': {
                        #     'base_score': '7',
                        #     'error_type': 'MEDIUM'
                        #     },
                        #     'cwe_ids': [''],
                        #     'cwe_name': 'N/A',
                        #     'solution': val.get('Description'),
                        #     'sources': [
                        #     'N/A'
                        #     ],
                        #     'error': error
                        # }
                        # self.result += set_custom_vul(**data)
                        
                        response = requests.get(f'https://cve.mitre.org/cgi-bin/cvekey.cgi?keyword={error.replace(" ","+")}')
                        soup = BeautifulSoup(response.text, "html.parser")
                        vuln_table = soup.find("div",{'id':'TableWithRules'})
                        if vuln_table:
                            rows = vuln_table.find_all('tr')
                            if rows and len(rows):
                                cols = rows[1].find_all('td')
                                if cols and len(cols):
                                    cve = cols[0].find(string=True)
                                    self.result += set_vul(cve, error, "nikto")
                        
                        
                        # self.result += set_vul_by_keyword(error, error)

                # ####################
                #  content end which update in future
                # ####################