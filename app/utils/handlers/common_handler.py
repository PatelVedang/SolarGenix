from .cve import CVE
from enum import Enum
import uuid
from bs4 import BeautifulSoup
import asyncio
import aiohttp
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
    error = kwargs.get('error')
    tool = kwargs.get('tool')
    alert_ref = kwargs.get('alert_ref')
    complexity = kwargs.get('complexity')
    alert_order = kwargs.get('alert_order')
    
    html_str = cve_obj.set_cve_html(**kwargs)

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
    return html_str

def set_vul_copy(**kwargs):
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
    alerts = kwargs.get('alerts',{})
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
                    <div class="col-3 border border-5 border-light {complexity}" data-id="complexity" data-instances="{value.get('instances')}" id="{alert_ref}" data-index="{self.alert_order}" data-tool="{tool}">
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
                        {value['wasc_id']}
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


def make_alert_obj(**kwargs):
    """
    The function `make_alert_obj` creates an alert object with various properties based on the provided
    keyword arguments.
    :return: an object with the following properties:
    """
    obj = {
    'complexity' : AlertSortOrder.sort_order.get(kwargs.get('complexity', '').lower()).get('label', 'Informational'),
    'alert_order' : AlertSortOrder.sort_order.get(kwargs.get('complexity', '').lower()).get('order', 0),
    'alert_ref' : str(uuid.uuid4()),
    'instances' : kwargs.get('instances',1),
    'error': kwargs.get('error'),
    'tool': kwargs.get('tool'),
    'evidence': kwargs.get('evidence','N/A').strip("\n").strip("-").strip().replace("\n","<br/>").replace(" ","&nbsp;"),
    'cwe_ids':  ",".join(kwargs.get('cwe_ids')).strip("\n").strip().replace("\n","<br/>").replace(" ","&nbsp;") if isinstance(kwargs.get('cwe_ids'), list) else 'N/A'
    }
    return obj


def alert_response(**kwargs):
    # alert type
    # 1 = seach by cve
    # 2 = seach by keyword
    # 3 = manual set cve
    # 4 = info_vulners
    # 5 = owasp

    alert_type = kwargs.get('alert_type')

    result = {}
    if alert_type == 1:
        alert_json = cve_obj.get_cve_details_by_id_v2(kwargs.get('cve'))
        if not alert_json:
            return result
        kwargs['complexity'] = alert_json.get('complexity','info')
        kwargs['cwe_ids'] = alert_json.get('cwe_ids',[])
        common_alert_data = make_alert_obj(**kwargs)
        result = {
            **result,
            **{
                kwargs.get('error') : {
                    **common_alert_data,
                    **{
                        'alert_json': alert_json,
                        'alert_template_generator': 'cve_template'
                    }
                }
            }
        }
    elif alert_type == 2:
        alert_json = cve_obj.get_cve_details_by_keyword_v2(kwargs.get('keyword'))
        kwargs['complexity'] = alert_json.get('complexity', 'info')
        kwargs['cwe_ids'] = alert_json.get('cwe_ids',[])
        common_alert_data = make_alert_obj(**kwargs)
        result = {
            **result,
            **{
                kwargs.get('error') : {
                    **common_alert_data,
                    **{
                        'alert_json': alert_json,
                        'alert_template_generator': 'cve_template'
                    }
                }
            }
        }
    elif alert_type == 3:
        common_alert_data = make_alert_obj(**kwargs)
        result = {
            **result,
            **{
                kwargs.get('error') : {
                    **common_alert_data,
                    **{
                        'alert_json': kwargs,
                        'alert_template_generator': 'cve_template'
                    }
                }
            }
        }
    elif alert_type == 4:
        common_alert_data = make_alert_obj(**kwargs)
        result = {
            **result,
            **{
                kwargs.get('error') : {
                    **common_alert_data,
                    **{
                        'alert_json': kwargs,
                        'alert_template_generator': 'info_template'
                    }
                }
            }
        }
    elif alert_type == 5:
        alerts = kwargs.get('alerts',[])
        for key,value in alerts.items():
            evidence = list(set(list(map(lambda x: x['evidence'],value.get('urls',[])))))
            if "\n".join(evidence):
                value['evidence'] = "\n".join(evidence)
            if value.get('cweid'):
                value['cwe_ids'] = [f"CWE-{value['cweid']}"]
            common_alert_data = make_alert_obj(**{**value,
                                                  **{
                                                      'complexity': value.get('risk'),
                                                      'error': value.get('name'),
                                                      'tool': kwargs.get('tool'),
                                                      'instances': value.get('instances',1)
                                                     }
                                                })
            result = {
                **result,
                **{
                    value.get('name') : {
                        **common_alert_data,
                        **{
                            'alert_json': value,
                            'alert_template_generator': 'zap_template'
                        }
                    }
                }
            }

    return result


class Templates:
    def templates(self, **kwargs):
        self.alert_ref = kwargs.get('alert_ref')
        self.alert_order = kwargs.get('alert_order')
        self.error = kwargs.get('error')
        self.tool = kwargs.get('tool')
        self.complexity = kwargs.get('complexity')

        template = kwargs.get('alert_template_generator')
        if template == "cve_template":
            return self.cve_template(**kwargs)
        elif template == "info_template":
            return self.info_template(**kwargs)
        elif template == "zap_template":
            return self.zap_template(**kwargs)
        
    def base_alert_html(self, html):
        """
        The function `base_alert_html` generates an HTML string with a specific structure and content
        based on the input parameters.
        
        :param html: The `html` parameter is a string that represents the HTML content that will be
        inserted into the `base_alert_html` template. It will be inserted into the `{html}` placeholder
        in the template
        :return: an HTML string.
        """
        html_str = f'''
        <div class="row mt-2">
            <div class="col-12 border border-5 border-light">
                <div class="row vul-header"">
                    <div class="col-3 border border-5 border-light {self.complexity}" data-id="complexity" data-instances="1" id="{self.alert_ref}" data-index="{self.alert_order}" data-tool="{self.tool}">
                        {self.complexity}
                    </div>
                    <div class="col-9 border border-5 border-light {self.complexity}" data-id="error">
                        {self.error}
                    </div>
                </div>
                {html}
                <div class="row">
                    <div class="col-3 border border-5 border-light body">
                        Tool
                    </div>
                    <div class="col-9 border border-5 border-light body">
                        {self.tool}
                    </div>
                </div>
            </div>
        </div>
        '''
        return html_str
    
    def cve_template(self, **kwargs):
        """
        The function `cve_template` generates an HTML string for a Common Vulnerabilities and Exposures
        (CVE) alert using the provided JSON data and returns it wrapped in a base alert HTML template.
        :return: the result of calling the `base_alert_html` method with the `html_str` as an argument.
        """
        html_str = cve_obj.set_cve_html(**kwargs.get('alert_json'))
        return self.base_alert_html(html_str)
        
    def info_template(self, **kwargs):
        """
        The `info_template` function generates an HTML template for displaying information about an
        alert, including risk factor, description, solution, and optionally, port.
        :return: the HTML string generated by the code.
        """
        alert_json = kwargs.get('alert_json',{})
        html_str = f'''
            <div class="row">
                <div class="col-3 border border-5 border-light body">
                    Risk Factor
                </div>
                <div class="col-9 border border-5 border-light body">
                    {alert_json.get('risk_factor', 'N/A')}
                </div>
            </div>
            <div class="row">
                <div class="col-3 border border-5 border-light body">
                    Description
                </div>
                <div class="col-9 border border-5 border-light body">
                    {alert_json.get('description')}
                </div>
            </div>
            <div class="row">
                <div class="col-3 border border-5 border-light body">
                    Solution
                </div>
                <div class="col-9 border border-5 border-light body">
                    {alert_json.get('solution', 'N/A')}
                </div>
            </div>'''
        if alert_json.get('port'):
            html_str += f'''
            <div class="row">
                <div class="col-3 border border-5 border-light body">
                    Port
                </div>
                <div class="col-9 border border-5 border-light body">
                    {alert_json.get('port')}
                </div>
            </div>
            '''
        return self.base_alert_html(html_str)

    def zap_template(self, **kwargs):
        """
        The function `zap_template` generates an HTML template based on the provided `alert_json`
        dictionary.
        :return: the HTML string generated by the code.
        """
        alert_json = kwargs.get('alert_json',{})
        html_str = f'''
            <div class="row">
                <div class="col-3 border border-5 border-light body">
                    Description
                </div>
                <div class="col-9 border border-5 border-light body">
                    {alert_json.get('description')}
                </div>
            </div>'''

        if alert_json.get('urls'):
            html_str += f'''
                <div class="row border border-5 border-light body py-1">
                </div>
            '''
            for url_obj in alert_json.get('urls'):
                html_str += f'''
                    <div class="row">
                        <div class="col-3 border border-5 border-light body pl-4">
                            URL
                        </div>
                        <div class="col-9 border border-5 border-light body">
                            {url_obj.get('url')}
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-3 border border-5 border-light body pl-5">
                            Method
                        </div>
                        <div class="col-9 border border-5 border-light body">
                            {url_obj.get('method')}
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-3 border border-5 border-light body pl-5">
                            Parameter
                        </div>
                        <div class="col-9 border border-5 border-light body">
                            {url_obj.get('parameter')}
                        </div>
                    </div><div class="row">
                        <div class="col-3 border border-5 border-light body pl-5">
                            Attack
                        </div>
                        <div class="col-9 border border-5 border-light body">
                            {url_obj.get('attack')}
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-3 border border-5 border-light body pl-5">
                            Evidence
                        </div>
                        <div class="col-9 border border-5 border-light body">
                            {url_obj.get('evidence')}
                        </div>
                    </div>
                '''
        html_str +=f'''
            <div class="row">
                <div class="col-3 border border-5 border-light body">
                    Instances
                </div>
                <div class="col-9 border border-5 border-light body">
                    {alert_json.get('instances')}
                </div>
            </div>
            <div class="row">
                <div class="col-3 border border-5 border-light body">
                    Solution
                </div>
                <div class="col-9 border border-5 border-light body">
                    {alert_json.get('solution')}
                </div>
            </div>
            <div class="row">
                <div class="col-3 border border-5 border-light body">
                    Reference
                </div>
                <div class="col-9 border border-5 border-light body">
                    {alert_json.get('reference')}
                </div>
            </div>
            <div class="row">
                <div class="col-3 border border-5 border-light body">
                    CWE Id
                </div>
                <div class="col-9 border border-5 border-light body">
                    <a href="https://cwe.mitre.org/data/definitions/{alert_json.get('cweid')}.html">{alert_json.get('cweid')}</a>
                </div>
            </div>
            <div class="row">
                <div class="col-3 border border-5 border-light body">
                    WASC Id
                </div>
                <div class="col-9 border border-5 border-light body">
                    {alert_json.get('wasc_id')}
                </div>
            </div>
            <div class="row">
                <div class="col-3 border border-5 border-light body">
                    Plugin Id
                </div>
                <div class="col-9 border border-5 border-light body">
                    <a href="https://www.zaproxy.org/docs/alerts/{alert_json.get('plugin_id')}/">{alert_json.get('plugin_id')}</a></td>
                </div>
            </div>
        '''
        return self.base_alert_html(html_str)