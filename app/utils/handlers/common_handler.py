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
    html_str, complexity= cve.set_cve_details(cve_str)
    
    html_str = f'''
    <div class="row">
        <div class="col-12 border border-5 border-light">
            <div class="row vul-header">
                <div class="col-3 border border-5 border-light {complexity}" data-id="complexity">
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

    <div class="row">
        <div class="col-12 border border-5 border-light">
            <div class="row vul-header">
                <div class="col-3 border border-5 border-light {complexity}" data-id="complexity">
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
    <div class="row">
        <div class="col-12 border border-5 border-light">
            <div class="row vul-header">
                <div class="col-3 border border-5 border-light {complexity}" data-id="complexity">
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
