from .cve import CVE
from enum import Enum
import uuid
cve_obj = CVE()


# The class AlertSortOrder defines a dictionary with keys representing different levels of alert
# severity and values representing their order and label.
class AlertSortOrder:
    sort_order = {
        'critical' : {'order': 0, 'label': 'Critical'},
        'high' : {'order': 1, 'label': 'High'},
        'medium' : {'order': 2, 'label': 'Medium'},
        'low' : {'order': 3, 'label': 'Low'},
        'info' : {'order': 4, 'label': 'Informational'},
        'informational' : {'order': 4, 'label': 'Informational'},
        'False-Positive' : {'order': 5, 'label': 'False-Positive'}
    }

def set_vul(**kwargs):
    """
    The function generates an HTML string containing information about a vulnerability, including its
    complexity and error message, based on input parameters.
    :return: a dictionary with a single key-value pair. The key is the string 'error' and the value is a
    dictionary containing information about the vulnerability/error, including an HTML string, an index,
    a complexity label, the number of instances, an alert reference, the tool used, and the error
    message.
    """
    """
    The function generates an HTML string containing information about a vulnerability, including its
    complexity and error message.

    This function will generate the html content of any vulnerability based on cve.
    
    :param cve_str: The CVE (Common Vulnerabilities and Exposures) string that identifies a specific
    vulnerability in a software or system
    :param error: The error parameter is a string that describes the vulnerability or error being
    reported
    :return: an HTML string that includes information about a CVE (Common Vulnerabilities and Exposures)
    vulnerability, including its complexity, error message, and details.
    """
    # complexity = cve_obj.get_complexity(cve_str)

    keyword = kwargs.get('keyword')
    custom = kwargs.get('custom')
    cve = kwargs.get('cve')
    error = kwargs.get('error')
    tool = kwargs.get('tool')
    alert_ref = str(uuid.uuid4())

    html_str = ""
    if keyword:
        html_str, complexity= cve_obj.set_cve_details_by_keyword_v1(keyword)
    elif custom:
        html_str, complexity = cve_obj.set_cve_html(**kwargs)
    else:
        html_str, complexity= cve_obj.set_cve_details_by_id_v2(cve)
    
    alert_order = AlertSortOrder.sort_order.get(complexity.lower()).get('order', 0)
    complexity = AlertSortOrder.sort_order.get(complexity.lower()).get('label', 'Informational')

    html_str = f'''
    <div class="row mt-2">
        <div class="col-12 border border-5 border-light">
            <div class="row vul-header"">
                <div class="col-3 border border-5 border-light {complexity}" data-id="complexity" data-instances="1" id="{alert_ref}" data-index="{alert_order}" data-tool="{tool}">
                    {complexity}
                </div>
                <div class="col-9 border border-5 border-light {complexity}" data-id="error">
                    {error}
                </div>
            </div>
            {html_str}
            <div class="row">
                <div class="col-3 border border-5 border-light body">
                    Tool
                </div>
                <div class="col-9 border border-5 border-light body">
                    {tool}
                </div>
            </div>
        </div>
    </div>
    '''
    return {error:
        {
            'html_data': html_str,
            'index': alert_order,
            'complexity': complexity,
            'instances': 1,
            'alert_ref': alert_ref,
            'tool': tool,
            'error':error
        }
    }

def set_info_vuln(**kwargs):
    """
    The function creates an HTML string with information about a vulnerability and returns it as a
    dictionary.
    :return: A dictionary with a single key-value pair, where the key is the value of the `error`
    parameter passed to the function, and the value is another dictionary with various information about
    the vulnerability, including an HTML string representation of the vulnerability, an index, a
    complexity label, the number of instances, an alert reference, the tool used, and the error message.
    """
    complexity = kwargs.get('complexity')
    error = kwargs.get('error')
    risk_factor = kwargs.get('risk_factor', 'N/A')
    desc = kwargs.get('desc')
    solution = kwargs.get('solution', 'N/A')
    port = kwargs.get('port')
    tool = kwargs.get('tool')
    alert_ref = str(uuid.uuid4())
    alert_order = AlertSortOrder.sort_order.get(complexity.lower()).get('order', 0)
    complexity = AlertSortOrder.sort_order.get(complexity.lower()).get('label', 'Informational')
    html_str = f'''

    <div class="row mt-2">
        <div class="col-12 border border-5 border-light">
            <div class="row vul-header" id="{alert_ref}">
                <div class="col-3 border border-5 border-light {complexity}" data-id="complexity" data-instances="1" id="{alert_ref}" data-index="{alert_order}" data-tool="{tool}">
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
    html_str +=f'''
            <div class="row">
                <div class="col-3 border border-5 border-light body">
                    Tool
                </div>
                <div class="col-9 border border-5 border-light body">
                    {tool}
                </div>
            </div>
        </div>
    </div>
    '''
    return {error:
        {
            'html_data': html_str,
            'index': alert_order,
            'complexity': complexity,
            'instances': 1,
            'alert_ref': alert_ref,
            'tool': tool,
            'error':error
        }
    }

def set_zap_template(**kwargs):
    """
    This function will generate the html content of owasp zap scan
    The function generates HTML code for a given set of alerts and tool information.
    :return: a dictionary containing information about alerts. The keys of the dictionary are the names
    of the alerts, and the values are dictionaries containing various information about the alerts, such
    as HTML data, index, complexity, instances, alert reference, tool, and error.
    """
    html_str = ""
    alerts = kwargs.get('alerts',[])
    tool = kwargs.get('tool')

    result = {}

    for key,value in alerts.items():
        alert_ref = str(uuid.uuid4())
        alert_order = AlertSortOrder.sort_order.get(value.get('risk').lower()).get('order', 0)
        complexity = AlertSortOrder.sort_order.get(value.get('risk').lower()).get('label', 'Informational')
        html_str = ""
        html_str += f'''
        <div class="row mt-2">
            <div class="col-12 border border-5 border-light">
                <div class="row vul-header" id="{alert_ref}">
                    <div class="col-3 border border-5 border-light {complexity}" data-id="complexity" data-instances="{value.get('instances')}" id="{alert_ref}" data-index="{alert_order}" data-tool="{tool}">
                        {complexity}
                    </div>
                    <div class="col-9 border border-5 border-light {complexity}" data-id="error">
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
                <div class="row">
                    <div class="col-3 border border-5 border-light body">
                        Tool
                    </div>
                    <div class="col-9 border border-5 border-light body">
                        {tool}
                    </div>
                </div>
            </div>
        </div>
        '''
        result = {**result,**
                    {
                        value.get('name'):
                        {
                            'html_data': html_str,
                            'index': alert_order,
                            'complexity': complexity,
                            'instances': value.get('instances',1),
                            'alert_ref': alert_ref,
                            'tool': tool,
                            'error':value.get('name')
                        }
                    }
                  }

    return result



