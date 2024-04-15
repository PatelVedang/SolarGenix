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
        'false-positive' : {'order': 5, 'label': 'False-Positive'}
    }

def set_cwe_ids(**kwargs):
    """
    The function `set_cwe_ids` takes keyword arguments and formats a list of CWE IDs into a string with
    specific replacements.
    :return: The function `set_cwe_ids` returns a string that contains the CWE IDs provided as input,
    separated by commas. If the input is not a list, it returns "N/A".
    """
    cwe_ids = "N/A"
    if isinstance(kwargs.get('cwe_ids'), list):
        cwe_ids = ",".join(kwargs.get('cwe_ids'))
        cwe_ids = cwe_ids.strip("\n")
        cwe_ids = cwe_ids.replace("\n","<br/>")
        cwe_ids = cwe_ids.replace(" ","&nbsp;")
    return cwe_ids

def set_evidence(**kwargs):
    """
    The function `set_evidence` takes keyword arguments and processes the 'evidence' value by stripping
    whitespace and newlines, replacing newlines with `<br/>`, and spaces with `&nbsp;`.
    :return: The function `set_evidence` takes keyword arguments and processes the 'evidence' argument
    to format it for display. It replaces newline characters with `<br/>`, spaces with `&nbsp;`, and
    removes leading and trailing whitespace and hyphens. The processed evidence is then returned.
    """
    evidence = "N/A"
    if kwargs.get('evidence'):
        evidence = kwargs.get('evidence')
        evidence = evidence.strip("\n")
        evidence = evidence.strip("-")
        evidence = evidence.strip()
        evidence = evidence.replace("\n","<br/>")
        evidence = evidence.replace(" ","&nbsp;")
    return evidence

def set_complexity(**kwargs):
    """
    The function `set_complexity` takes keyword arguments and returns the corresponding complexity label
    in lowercase if provided, defaulting to "Informational" if not.
    :return: The function `set_complexity` is returning the complexity level based on the input provided
    in the `kwargs`. If the `complexity` key is present in the `kwargs`, it will retrieve the
    corresponding complexity level from `AlertSortOrder.sort_order` dictionary, convert it to lowercase,
    and then return the label of the complexity level. If the `complexity` key is not present or the
    """
    complexity = ""
    if kwargs.get('complexity'):
        complexity = kwargs.get('complexity', '').lower()
        complexity = AlertSortOrder.sort_order.get(complexity)
        complexity = complexity.get('label', 'Informational')
    return complexity

def set_alert_order(**kwargs):
    """
    The function `set_alert_order` takes keyword arguments and returns the corresponding alert order
    based on complexity.
    :return: The function `set_alert_order` is returning the sort order for alerts based on the
    complexity provided in the keyword arguments. If the complexity is provided, it will retrieve the
    corresponding sort order from the `AlertSortOrder.sort_order` dictionary, convert it to lowercase,
    and then return the order value. If no complexity is provided or if the complexity does not match
    any key in the dictionary, it will
    """
    alert_order = ""
    if kwargs.get('complexity'):
        alert_order = kwargs.get('complexity','').lower()
        alert_order = AlertSortOrder.sort_order.get(alert_order, '')
        alert_order = alert_order.get('order', 0)
    return alert_order

def make_alert_obj(**kwargs):
    """
    The function `make_alert_obj` creates an alert object with various properties based on the provided
    keyword arguments.
    :return: an object with the following properties:
    """
    obj = {
    'complexity': set_complexity(**kwargs),
    'alert_order': set_alert_order(**kwargs),
    'alert_ref' : str(uuid.uuid4()),
    'instances' : kwargs.get('instances',1),
    'error': kwargs.get('error'),
    'tool': kwargs.get('tool'),
    'evidence': set_evidence(**kwargs),
    'cwe_ids': set_cwe_ids(**kwargs)
    # 'complexity' : AlertSortOrder.sort_order.get(kwargs.get('complexity', '').lower()).get('label', 'Informational'),
    # 'alert_order' : AlertSortOrder.sort_order.get(kwargs.get('complexity', '').lower()).get('order', 0),
    # 'evidence': kwargs.get('evidence','N/A').strip("\n").strip("-").strip().replace("\n","<br/>").replace(" ","&nbsp;"),
    # 'cwe_ids':  ",".join(kwargs.get('cwe_ids')).strip("\n").strip().replace("\n","<br/>").replace(" ","&nbsp;") if isinstance(kwargs.get('cwe_ids'), list) else 'N/A'
    }
    return obj


async def alert_response(**kwargs):
    # alert type
    # 1 = seach by cve
    # 2 = seach by keyword
    # 3 = manual set cve
    # 4 = info_vulners
    # 5 = owasp

    alert_type = kwargs.get('alert_type')

    result = {}
    if alert_type == 1:
        alert_json = await cve_obj.get_cve_details_by_id_v2(kwargs.get('cve'))
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
        alert_json = await cve_obj.get_cve_details_by_keyword_v2(kwargs.get('keyword'))
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
        alerts = kwargs.get('alerts',{})
        for key,value in alerts.items():
            evidence = list(set(list(map(lambda x: x['evidence'],value.get('urls',[])))))
            if "\n".join(evidence):
                value['evidence'] = "\n".join(evidence)
            if value.get('cweid'):
                value['cwe_ids'] = [f"CWE-{value['cweid']}"]
            common_alert_data = make_alert_obj(**{**value,
                                                  **{
                                                      'complexity': value.get('risk') if value.get('risk') else 'info',
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