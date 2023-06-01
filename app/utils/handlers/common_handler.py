from .cve import CVE
cve = CVE()

def set_vul(cve_str, error):
    """
    The function generates an HTML string containing information about a vulnerability, including its
    complexity and error message.
    
    :param cve_str: The CVE (Common Vulnerabilities and Exposures) string that identifies a specific
    vulnerability in a software or system
    :param error: The error parameter is a string that describes the vulnerability or error being
    reported
    :return: an HTML string that includes information about a CVE (Common Vulnerabilities and Exposures)
    vulnerability, including its complexity, error message, and details.
    """
    # complexity = cve.get_complexity(cve_str)

    html_str = ""
    html_str, complexity= cve.set_cve_details_by_id_v2(cve_str)
    
    html_str = f'''
    <div class="row mt-2">
        <div class="col-12 border border-5 border-light">
            <div class="row vul-header">
                <div class="col-3 border border-5 border-light {complexity}" data-id="complexity" data-instances="1">
                    {complexity}
                </div>
                <div class="col-9 border border-5 border-light {complexity}" data-id="error">
                    {error}
                </div>
            </div>
            {html_str}
        </div>
    </div>
    '''
    return html_str


def set_vul_by_keyword(keyword, error):
    """
    The function sets CVE details by a given keyword and returns an HTML string with the details and
    error message.
    
    :param keyword: The keyword is a string that is used to search for relevant CVE (Common
    Vulnerabilities and Exposures) details
    :param error: The error parameter is a string that represents the error message associated with a
    vulnerability
    :return: a string variable named `html_str`. If the `html_str` variable is not empty, it will
    contain an HTML code that displays the details of a CVE (Common Vulnerabilities and Exposures) based
    on a given keyword, along with the complexity and error information. If the `html_str` variable is
    empty, it means that no CVE details were found for the given
    """
    html_str = ""
    html_str, complexity= cve.set_cve_details_by_keyword_v1(keyword)
    if html_str:
        html_str = f'''
        <div class="row mt-2">
            <div class="col-12 border border-5 border-light">
                <div class="row vul-header">
                    <div class="col-3 border border-5 border-light {complexity}" data-id="complexity" data-instances="1">
                        {complexity}
                    </div>
                    <div class="col-9 border border-5 border-light {complexity}" data-id="error">
                        {error}
                    </div>
                </div>
                {html_str}
            </div>
        </div>
        '''
    return html_str

def set_info_vuln(**kwargs):
    """
    The function generates an HTML string containing information about a vulnerability, based on the
    input parameters.
    :return: an HTML string that contains information about a vulnerability. The information includes
    the complexity, error, risk factor, description, and solution. The HTML string is formatted using
    Bootstrap classes to create a visually appealing layout.
    """
    complexity = kwargs.get('complexity')
    error = kwargs.get('error')
    risk_factor = kwargs.get('risk_factor', 'N/A')
    desc = kwargs.get('desc')
    solution = kwargs.get('solution', 'N/A')
    port = kwargs.get('port')
    html_str = f'''

    <div class="row mt-2">
        <div class="col-12 border border-5 border-light">
            <div class="row vul-header">
                <div class="col-3 border border-5 border-light {complexity}" data-id="complexity" data-instances="1">
                    {complexity}
                </div>
                <div class="col-9 border border-5 border-light {complexity}" data-id="error">
                    {error}
                </div>
            </div>
            <div class="row">
                <div class="col-3 border border-5 border-light body">
                    Risk Factor
                </div>
                <div class="col-9 border border-5 border-light body">
                    {risk_factor}
                </div>
            </div>
            <div class="row">
                <div class="col-3 border border-5 border-light body">
                    Description
                </div>
                <div class="col-9 border border-5 border-light body">
                    {desc}
                </div>
            </div>
            <div class="row">
                <div class="col-3 border border-5 border-light body">
                    Solution
                </div>
                <div class="col-9 border border-5 border-light body">
                    {solution}
                </div>
            </div>'''
    if port:
        html_str += f'''
        <div class="row">
            <div class="col-3 border border-5 border-light body">
                Port
            </div>
            <div class="col-9 border border-5 border-light body">
                {port}
            </div>
        </div>
        '''
    html_str +='''
        </div>
    </div>
    '''
    return html_str

def set_custom_vul(**kwargs):
    """
    The function generates HTML code for a custom vulnerability with a given complexity and error
    message.
    :return: an HTML string that includes information about a custom vulnerability. The HTML string
    includes a header with the complexity level and error message, as well as the HTML string generated
    by the `set_cve_html` function.
    """
    html_str = ""
    html_str, complexity = cve.set_cve_html(**kwargs)
    
    html_str = f'''
    <div class="row mt-2">
        <div class="col-12 border border-5 border-light">
            <div class="row vul-header">
                <div class="col-3 border border-5 border-light {complexity}" data-id="complexity" data-instances="1">
                    {complexity}
                </div>
                <div class="col-9 border border-5 border-light {complexity}" data-id="error">
                    {kwargs.get('error')}
                </div>
            </div>
            {html_str}
        </div>
    </div>
    '''

    return html_str

def set_zap_template(**kwargs):
    """
    The function generates an HTML string for a ZAP security report template based on input alerts.
    :return: a string of HTML code that creates a template for displaying information about alerts. The
    template includes information such as the risk level, name, description, URLs, instances, solution,
    reference, CWE ID, WASC ID, and plugin ID for each alert. The information is passed to the function
    as keyword arguments in a dictionary format.
    """
    html_str = ""
    alerts = kwargs.get('alerts',[])
    for key,value in alerts.items():
        html_str += f'''
        <div class="row mt-2">
            <div class="col-12 border border-5 border-light">
                <div class="row vul-header">
                    <div class="col-3 border border-5 border-light {value.get('risk')}" data-id="complexity" data-instances="{value.get('instances')}">
                        {value.get('risk')}
                    </div>
                    <div class="col-9 border border-5 border-light {value.get('risk')}" data-id="error">
                        {value.get('name')}
                    </div>
                </div>
                <div class="row">
                    <div class="col-3 border border-5 border-light body">
                        Description
                    </div>
                    <div class="col-9 border border-5 border-light body">
                        {value.get('description')}
                    </div>
                </div>'''
        if value.get('urls'):
            html_str += f'''
                <div class="row border border-5 border-light body py-1">
                </div>
            '''
            for url_obj in value.get('urls'):
                html_str += f'''
                <div class="row">
                    <div class="col-3 border border-5 border-light body pl-4">
                        URL
                    </div>
                    <div class="col-9 border border-5 border-light body">
                        {url_obj['url']}
                    </div>
                </div><div class="row">
                    <div class="col-3 border border-5 border-light body pl-5">
                        Method
                    </div>
                    <div class="col-9 border border-5 border-light body">
                        {url_obj['method']}
                    </div>
                </div>
                <div class="row">
                    <div class="col-3 border border-5 border-light body pl-5">
                        Parameter
                    </div>
                    <div class="col-9 border border-5 border-light body">
                        {url_obj['parameter']}
                    </div>
                </div><div class="row">
                    <div class="col-3 border border-5 border-light body pl-5">
                        Attack
                    </div>
                    <div class="col-9 border border-5 border-light body">
                        {url_obj['attack']}
                    </div>
                </div>
                <div class="row">
                    <div class="col-3 border border-5 border-light body pl-5">
                        Evidence
                    </div>
                    <div class="col-9 border border-5 border-light body">
                        {url_obj['evidence']}
                    </div>
                </div>
                '''
        html_str +=f'''
                <div class="row">
                    <div class="col-3 border border-5 border-light body">
                        Instances
                    </div>
                    <div class="col-9 border border-5 border-light body">
                        {value['instances']}
                    </div>
                </div>
                <div class="row">
                    <div class="col-3 border border-5 border-light body">
                        Solution
                    </div>
                    <div class="col-9 border border-5 border-light body">
                        {value['solution']}
                    </div>
                </div>
                <div class="row">
                    <div class="col-3 border border-5 border-light body">
                        Reference
                    </div>
                    <div class="col-9 border border-5 border-light body">
                        {value['reference']}
                    </div>
                </div>
                <div class="row">
                    <div class="col-3 border border-5 border-light body">
                        CWE Id
                    </div>
                    <div class="col-9 border border-5 border-light body">
                        <a href="https://cwe.mitre.org/data/definitions/{value['cweid']}.html">{value['cweid']}</a>
                    </div>
                </div>
                <div class="row">
                    <div class="col-3 border border-5 border-light body">
                        WASC Id
                    </div>
                    <div class="col-9 border border-5 border-light body">
                        {value['wascid']}
                    </div>
                </div>
                <div class="row">
                    <div class="col-3 border border-5 border-light body">
                        Plugin Id
                    </div>
                    <div class="col-9 border border-5 border-light body">
                        <a href="https://www.zaproxy.org/docs/alerts/{value['plugin_id']}/">{value['plugin_id']}</a></td>
                    </div>
                </div>
            </div>
        </div>
        '''

    return html_str



