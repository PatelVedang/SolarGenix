from celery import Celery
import subprocess
from .models import Target, TargetLog
import platform
import requests
from celery import shared_task
import logging
logger = logging.getLogger('django')
from django.conf import settings
from datetime import datetime
import threading
from tldextract import extract
import time
import signal
import json
import pandas as pd

from zapv2 import ZAPv2
zap = ZAPv2()

def update_target_and_add_log(**kwargs):
    """
    The function updates a target object with a raw result and status, and creates a TargetLog object
    with the target ID and action.
    """
    if kwargs.get('scan_time'):
        kwargs.get('target').update(scan_time=kwargs.get('scan_time'))
    if kwargs.get('output'):
        kwargs.get('target').update(raw_result=kwargs.get('output'), status=kwargs.get('status'))
    else:
        kwargs.get('target').update(status=kwargs.get('status'))
    TargetLog.objects.create(target=Target(kwargs.get('id')), action=kwargs.get('action'))

def get_scan_time(end_date=datetime.utcnow(), **kwargs):
    return round(((end_date - kwargs.get('start_time')).total_seconds()), 2)

c = Celery('proj')
@c.task
def scan(id, time_limit, token, order_id, batch_scan):
    thread = threading.Thread(target=send_message, args=(id, token, order_id, batch_scan))
    thread.start()

    py_tools={
        'owasp_zap':OWASP_ZAP_spider_scan_v3
        # 'owasp_zap':OWASP_ZAP_active_scan_v1
    }

    target = Target.objects.filter(id=id)
    ip = ".".join(list(extract(target[0].ip))).strip(".")
    logger.info(f"====>>>>>>>>       \nIP:{ip} with id:{id} added to queue\n       <<<<<<<<====")
    output = ""
    tool_cmd = target[0].tool.tool_cmd
    time_limit = target[0].tool.time_limit
    pwd = settings.SUDO_PWD
    # add sudo access for those tools which need to run tool
    if target[0].tool.sudo_access:
        tool_cmd = f'echo {pwd} | sudo -S {tool_cmd}'
    
    # Only one of the three conditions is true at once.
    if (tool_cmd.find("<ip>")>=0) or (tool_cmd.find("<IP>")>=0):
        # Here we are scan remote domain with custom ip option
        tool_cmd = tool_cmd.replace("<ip>",ip).replace("<IP>",ip)
    elif (tool_cmd.find("<domain>")>=0) or (tool_cmd.find("<DOMAIN>")>=0):
        # Here we are scan remote domain with custom root domain option
        root_domain = ".".join(list(extract(ip))[-2:]).strip(".")
        tool_cmd = tool_cmd.replace("<domain>",root_domain).replace("<DOMAIN>",root_domain)
    else:
        # Default we are going with plain url
        tool_cmd += f' {ip}'
    
    if target[0].status >= 1:
        try:
            logger.info(f"====>>>>>>>>       \nScanning began for IP:{ip} with id:{id}\n       <<<<<<<<====")
            target.update(status = 2)
            start_time = datetime.utcnow()
            if target[0].tool.py_tool:
                tool_cmd = target[0].tool.tool_cmd
                if py_tools.get(tool_cmd):

                    # Set the timeout signal and handler
                    signal.signal(signal.SIGALRM, timeout_handler)
                    signal.alarm(time_limit)
                    
                    output = py_tools.get(tool_cmd)(ip)
                else:
                    raise ModuleNotFoundError(f"{tool_cmd} tool does not exist.")
            else:
                if platform.uname().system == 'Windows':
                    # output = subprocess.check_output(f"{tool_cmd} {ip}", shell=False, timeout=time_limit).decode('utf-8')
                    output = subprocess.run(f"{tool_cmd}", shell=False, capture_output=True, timeout=time_limit)
                else:
                    # output = subprocess.check_output(f"{tool_cmd} {ip}", shell=True, timeout=time_limit).decode('utf-8')
                    output = subprocess.run(f"{tool_cmd}", shell=True, capture_output=True, timeout=time_limit)
                
                if output.stderr.decode('utf-8') and not output.stdout.decode('utf-8'):
                    logger.info(f"====>>>>>>>>       \nBackground thread for ip:{ip} with id:{id} has been terminated due to tool issue.\n       <<<<<<<<====")
                    update_target_and_add_log(target=target, output=output.stderr.decode('utf-8'), id=id, status=3, action=3, scan_time = get_scan_time(start_time=start_time, end_date=datetime.utcnow()))
                    return False
                output=output.stdout.decode('utf-8')
                
        except subprocess.TimeoutExpired as e:
            if e.output:
                error = f'\n{e.output.decode("utf-8")}{str(e)}'
            else:
                error = f'{str(e)}'

            logger.info(f"====>>>>>>>>       \nBackground thread for ip:{ip} with id:{id} has been terminated\n       <<<<<<<<====")
            update_target_and_add_log(target=target, output=str(error), id=id, status=3, action=3, scan_time = get_scan_time(start_time=start_time, end_date=datetime.utcnow()))
            return False
        except Exception as e:
            import traceback
            traceback.print_exc()
            logger.info(f"====>>>>>>>>       \nBackground thread for ip:{ip} with id:{id} has been terminated\n       <<<<<<<<====")
            update_target_and_add_log(target=target, output=str(e), id=id, status=3, action=3, scan_time = get_scan_time(start_time=start_time, end_date=datetime.utcnow()))
            return False
        update_target_and_add_log(target=target, output=output, id=id, status=4, action=4, scan_time = get_scan_time(start_time=start_time, end_date=datetime.utcnow()))
        return True
    else:
        return False

def send_message(id, token, order_id, batch_scan):
    """
    This function sends a request to the API to send a message to the target user
    
    :param id: The id of the target user
    :param token: The token you get from the login API
    """
    if batch_scan:
        if not Target.objects.filter(order_id=order_id).exclude(id=id).filter(status__in=[2]).count():
            logger.info(f"====>>>>>>>>       \nWebsocket API trigger for order_id:{order_id}\n       <<<<<<<<====")
            response = requests.get(f'http://localhost:8000/api/sendMessage/?order={order_id}', headers={'Authorization': token})
    else:
        logger.info(f"====>>>>>>>>       \nWebsocket API trigger for target id:{id}\n       <<<<<<<<====")
        response = requests.get(f'http://localhost:8000/api/sendMessage/?id={id}', headers={'Authorization': token})

    return True

def OWASP_ZAP_spider_scan_v1(url):
    # Generating a report based on alerts received with message and alert ids
    # Here we are storing html as a scan result(raw result)
    if not ('http://' in url or 'https://' in url):
        url = f"http://{url}"

    # create a new instance of the ZAP API client
    
    risk_levels = {
        'High': {'class':'risk-3', 'count':0},
        'Medium': {'class':'risk-2', 'count':0},
        'Low': {'class':'risk-1', 'count':0},
        'Informational': {'class':'risk-0', 'count':0},
        'False Positives:': {'class':'risk--1', 'count':0},
    }

    spider_scan_id = zap.spider.scan(url)
    
    while int(zap.spider.status(spider_scan_id)) < 100:
        # print('Spider scan progress %: {} for scan id {} with url {}'.format(zap.spider.status(spider_scan_id), spider_scan_id, url))
        time.sleep(1)

    # to get all alerts message ids
    full_results = zap.spider.full_results(spider_scan_id)

    alerts = {}
    
    if isinstance(full_results,list) and len(full_results):
        for obj in full_results[0].get('urlsInScope',[]):
            message_id = obj.get('messageId')
            alert_obj = zap.core.alert(message_id)
            if isinstance(alert_obj,dict):
                alert_title = alert_obj.get('name')
                custom_alert_obj = {
                    'name': alert_obj.get('name'),
                    'description' : alert_obj.get('description'),
                    'urls':[
                        {
                        'url' : alert_obj.get('url'),
                        'method': alert_obj.get('method'),
                        'parameter': alert_obj.get('param'),
                        'attack': alert_obj.get('attack'),
                        'evidence': alert_obj.get('evidence'),
                        }
                    ],
                    'instances': 1,
                    'wsac_id': alert_obj.get('wascid'),
                    'cweid': alert_obj.get('cweid'),
                    'plugin_id': alert_obj.get('pluginId'),
                    'reference': "<br>".join(alert_obj.get('reference').split("\n")),
                    'solution': alert_obj.get('solution'),
                    'risk': alert_obj.get('risk')
                }

                if alert_title and alerts.get(alert_title):
                    custom_alert_obj['urls'] = [*alerts[alert_title]['urls'], *custom_alert_obj['urls']]
                    custom_alert_obj['instances'] = alerts[alert_title]['instances']+1
                else:
                    risk_levels[custom_alert_obj['risk']]['count'] += 1
                
                alerts[alert_title] = custom_alert_obj

    
    # Clean spider scan result
    zap.spider.remove_scan(scanid=spider_scan_id)

    # Generate report
    return set_zap_html_report(url, risk_levels, alerts)

def OWASP_ZAP_spider_scan_v2(url):
    # To store html as a scan result(raw_result)
    if not ('http://' in url or 'https://' in url):
        url = f"http://{url}"
    # risk_levels object to get alerts count riks wise
    risk_levels = {
        'High': {'class':'risk-3', 'count':0},
        'Medium': {'class':'risk-2', 'count':0},
        'Low': {'class':'risk-1', 'count':0},
        'Informational': {'class':'risk-0', 'count':0},
        'False Positives:': {'class':'risk--1', 'count':0},
    }
    # scan url with spider tool of OWASP ZAP fro quick scan
    spider_scan_id = zap.spider.scan(url=url)
    
    # Here we are checking if spider scan still in progress then current process is sleep for 1s until 100% is compelete
    while int(zap.spider.status(spider_scan_id)) < 100:
        print('Spider scan progress %: {} for scan id {} with url {}'.format(zap.spider.status(spider_scan_id), spider_scan_id, url))
        time.sleep(10)

    # custom alert object
    alerts = {}
    
    alerts_list = zap.core.alerts(baseurl=url)
    for alert_obj in alerts_list:
        if isinstance(alert_obj,dict):
            alert_title = alert_obj.get('name')
            # Making json object to generate html report 
            custom_alert_obj = {
                'name': alert_obj.get('name'),
                'description' : alert_obj.get('description'),
                'urls':[
                    {
                    'url' : alert_obj.get('url'),
                    'method': alert_obj.get('method'),
                    'parameter': alert_obj.get('param'),
                    'attack': alert_obj.get('attack'),
                    'evidence': alert_obj.get('evidence'),
                    }
                ],
                'instances': 1,
                'wsac_id': alert_obj.get('wascid') if alert_obj.get('wascid')=="-1" else "",
                'cweid': alert_obj.get('cweid') if alert_obj.get('cweid')=="-1" else "",
                'plugin_id': alert_obj.get('pluginId'),
                'reference': "<br>".join(alert_obj.get('reference').split("\n")),
                'solution': alert_obj.get('solution'),
                'risk': alert_obj.get('risk')
            }

            if alert_title and alerts.get(alert_title):
                custom_alert_obj['urls'] = [*alerts[alert_title]['urls'], *custom_alert_obj['urls']]
                custom_alert_obj['instances'] = alerts[alert_title]['instances']+1
            else:
                risk_levels[custom_alert_obj['risk']]['count'] += 1
            
            alerts[alert_title] = custom_alert_obj

    # Clean spider scan result
    zap.spider.remove_scan(scanid=spider_scan_id)

    # Generate report
    return set_zap_html_report(url, risk_levels, alerts)

def OWASP_ZAP_spider_scan_v3(url):
    # To store json as a scan result

    # risk_levels object to get alerts count riks wise
    risk_levels = {
        'High': {'class':'risk-3', 'count':0},
        'Medium': {'class':'risk-2', 'count':0},
        'Low': {'class':'risk-1', 'count':0},
        'Informational': {'class':'risk-0', 'count':0},
        'False Positives:': {'class':'risk--1', 'count':0},
    }

    domain = ".".join(list(extract(url))).strip(".")
    http_url = f"http://{domain}"
    https_url = f"https://{domain}"
    start_time = datetime.utcnow()
    
    if not ('http://' in url or 'https://' in url):
        url = http_url
    
    # scan url with spider tool of OWASP ZAP fro quick scan
    spider_scan_id = zap.spider.scan(url=url)
    
    # Here we are checking if spider scan still in progress then current process is sleep for 1s until 100% is compelete
    while int(zap.spider.status(spider_scan_id)) < 100:
        print('Spider scan progress %: {} for scan id {} with url {}'.format(zap.spider.status(spider_scan_id), spider_scan_id, url))
        time.sleep(1)

    
    # All message id objects for current scan
    full_results = pd.DataFrame(data=zap.spider.full_results(scanid=spider_scan_id))
    spider_requests = pd.DataFrame(data=[*full_results.loc[full_results.index[0]]['urlsInScope'], *full_results.loc[full_results.index[2]]['urlsIoError']])
    spider_msg_ids = spider_requests['messageId'].to_list()
    spider_msg_ids.sort()
    
    alerts = []
    counter = 0
    while True:
        # All alerts of specific base url
        alerts = pd.DataFrame(data=[*zap.alert.alerts(baseurl=http_url), *zap.alert.alerts(baseurl=https_url)])
        if len(alerts.columns) and 'messageId' in alerts.columns:
            alert_message_ids = alerts['messageId'].tolist()
            alert_message_ids.sort()
        else:
            alert_message_ids = []
        matched_msg_ids  = sorted(list(set(alert_message_ids).intersection(spider_msg_ids)))
        if matched_msg_ids==spider_msg_ids:
            print("Match found")
            break
        else:
            if counter==10:
                print("Match not found")
                break
            counter += 1
            time.sleep(int(settings.SPIDER_API_CALL_DELAY))
            continue
    
    # Alerts with message Id(We are accessing alerts based on message id to delete specific alerts of single scan) 
    alert_with_msg_ids = {}
    
    # Update in future
    if len(alerts):
        for alert in alerts.to_dict('records'):
            alert_with_msg_ids[alert.get('messageId')] = {**alert_with_msg_ids.get(alert.get('messageId'),{}), **{alert.get('id'):alert}}

    # custom alert object
    alerts = {}
    
    if len(spider_requests) and len(alert_with_msg_ids.keys()):
        for obj in spider_requests.to_dict('records'):
            message_id = obj.get('messageId')
            if alert_with_msg_ids.get(message_id):
                for alert_key, alert_obj in alert_with_msg_ids.get(message_id).items():
                    if isinstance(alert_obj,dict):
                        alert_title = alert_obj.get('name')
                        custom_alert_obj = {
                            'name': alert_obj.get('name'),
                            'description' : alert_obj.get('description'),
                            'urls':[
                                {
                                'url' : alert_obj.get('url'),
                                'method': alert_obj.get('method'),
                                'parameter': alert_obj.get('param'),
                                'attack': alert_obj.get('attack'),
                                'evidence': alert_obj.get('evidence'),
                                }
                            ],
                            'instances': 1,
                            'wasc_id': alert_obj.get('wascid') if alert_obj.get('wascid')!="-1" else "",
                            'cweid': alert_obj.get('cweid') if alert_obj.get('cweid')!="-1" else "",
                            'plugin_id': alert_obj.get('pluginId'),
                            'reference': "<br>".join(alert_obj.get('reference').split("\n")),
                            'solution': alert_obj.get('solution'),
                            'risk': alert_obj.get('risk')
                        }

                        if alert_title and alerts.get(alert_title):
                            custom_alert_obj['urls'] = [*alerts[alert_title]['urls'], *custom_alert_obj['urls']]
                            custom_alert_obj['instances'] = alerts[alert_title]['instances']+1
                        else:
                            risk_levels[custom_alert_obj['risk']]['count'] += 1
                        
                        alerts[alert_title] = custom_alert_obj
                    zap.alert.delete_alert(id=alert_key)
    
    # Remove spider scan
    zap.spider.remove_scan(scanid=spider_scan_id)

    return json.dumps({'alerts': alerts, 'risk_levels': risk_levels})

def timeout_handler(signum, frame):
    raise TimeoutError("Timeout occurred")

def OWASP_ZAP_active_scan_v1(url):
    # To store json as a scan result in active scan
    if not ('http://' in url or 'https://' in url):
        url = f"http://{url}"
    # risk_levels object to get alerts count riks wise
    risk_levels = {
        'High': {'class':'risk-3', 'count':0},
        'Medium': {'class':'risk-2', 'count':0},
        'Low': {'class':'risk-1', 'count':0},
        'Informational': {'class':'risk-0', 'count':0},
        'False Positives:': {'class':'risk--1', 'count':0},
    }
    # scan url with active tool of OWASP ZAP fro quick scan
    scan_id = zap.ascan.scan(url=url)
    
    # Here we are checking if spider scan still in progress then current process is sleep for 1s until 100% is compelete
    while int(zap.ascan.status(scan_id)) < 100:
        print('Active scan progress %: {} for scan id {} with url {}'.format(zap.ascan.status(scan_id), scan_id, url))
        time.sleep(10)

    # All alerts of single current active scan
    alerts_ids = zap.ascan.alerts_ids(scanid=scan_id)

    # custom alert object
    alerts = {}
    for alert_id in alerts_ids:
        alert_obj = zap.core.alert(id=alert_id)
        if isinstance(alert_obj,dict):
            alert_title = alert_obj.get('name')
            custom_alert_obj = {
                'name': alert_obj.get('name'),
                'description' : alert_obj.get('description'),
                'urls':[
                    {
                    'url' : alert_obj.get('url'),
                    'method': alert_obj.get('method'),
                    'parameter': alert_obj.get('param'),
                    'attack': alert_obj.get('attack'),
                    'evidence': alert_obj.get('evidence'),
                    }
                ],
                'instances': 1,
                'wsac_id': alert_obj.get('wascid') if alert_obj.get('wascid')!="-1" else "",
                'cweid': alert_obj.get('cweid') if alert_obj.get('cweid')!="-1" else "",
                'plugin_id': alert_obj.get('pluginId'),
                'reference': "<br>".join(alert_obj.get('reference').split("\n")),
                'solution': alert_obj.get('solution'),
                'risk': alert_obj.get('risk')
            }

            if alert_title and alerts.get(alert_title):
                custom_alert_obj['urls'] = [*alerts[alert_title]['urls'], *custom_alert_obj['urls']]
                custom_alert_obj['instances'] = alerts[alert_title]['instances']+1
            else:
                risk_levels[custom_alert_obj['risk']]['count'] += 1
            
            alerts[alert_title] = custom_alert_obj
        zap.core.delete_alert(alert_id)

    zap.ascan.remove_scan(scanid=scan_id)

    return json.dumps({'alerts': alerts, 'risk_levels': risk_levels})

# Currently we are not using this one
def set_zap_html_report(url, risk_levels, alerts):
    alerts_html = ""
    alert_details_html = ""

    # set alerts with alerts details
    for key,value in alerts.items():
        # Individual alert title table html
        alerts_html += f'''
            <tr>
				<td><a href="">{key}</a></td>
				<td align="center" class="{risk_levels[value['risk']]['class']}">{value['risk']}</td>
				<td align="center">{value['instances']}</td>
			</tr>
        '''

        # Individual alert detail html
        alert_details_html += f'''
            <table class="results">
				<tr height="24">
					<th width="20%" class="{risk_levels[value['risk']]['class']}"><a
						id="10202"></a>
						<div>{value['risk']}</div></th>
					<th class="{risk_levels[value['risk']]['class']}">{key}</th>
				</tr>
				<tr>
					<td width="20%">Description</td>
					<td width="80%">
							<div>{value['description']}</div>
				</tr>'''
        if value.get('urls'):
            alert_details_html += '''<TR vAlign="top">
                <TD colspan="2"></TD>
            </TR>'''
			
            # Setting each url in single alert
            for url_obj in value.get('urls'):
                alert_details_html += f'''<tr>
						<td width="20%"
							class="indent1">URL</td>
						<td width="80%">{url_obj['url']}</td>
					</tr>
					<tr>
						<td width="20%"
							class="indent2">Method</td>
						<td width="80%">{url_obj['method']}</td>
					</tr>
					<tr>
						<td width="20%"
							class="indent2">Parameter</td>
						<td width="80%">{url_obj['parameter']}</td>
					</tr>
					<tr>
						<td width="20%"
							class="indent2">Attack</td>
						<td width="80%">{url_obj['attack']}</td>
					</tr>
					<tr>
						<td width="20%"
							class="indent2">Evidence</td>
						<td width="80%">{url_obj['evidence']}</td>
					</tr>'''
				
        alert_details_html += f'''<tr>
					<td width="20%">Instances</td>
					<td width="80%">{value['instances']}</td>
				</tr>
				<tr>
					<td width="20%">Solution</td>
					<td width="80%">
							<div>{value['solution']}</div>
						</td>
				</tr>
				<tr>
					<td width="20%">Reference</td>
					<td width="80%">
                        {value['reference']}
                    </td>
				</tr>
				<tr>
					<td width="20%">CWE Id</td>
					<td width="80%"><a
						href="https://cwe.mitre.org/data/definitions/{value['cweid']}.html">{value['cweid']}</a></td>
				</tr>
				<tr>
					<td width="20%">WASC Id</td>
					<td width="80%">{value['wsac_id']}</td>
				</tr>
				<tr>
					<td width="20%">Plugin Id</td>
					<td width="80%"><a
						href="https://www.zaproxy.org/docs/alerts/{value['plugin_id']}/">{value['plugin_id']}</a></td>
				</tr>
			</table>
			<div class="spacer"></div>
        '''

    # main body
    html_str = '''
        <!DOCTYPE html>
        <html>
        <head>
        <META http-equiv="Content-Type" content="text/html; charset=UTF-8" />
        <title>ZAP Scanning Report</title>
        <style type="text/css">
        body {
            font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
            color: #000;
            font-size: 13px;
        }

        h1 {
            text-align: center;
            font-weight: bold;
            font-size: 32px
        }

        h3 {
            font-size: 16px;
        }

        table {
            border: none;
            font-size: 13px;
        }

        td, th {
            padding: 3px 4px;
            word-break: break-word;
        }

        th {
            font-weight: bold;
            background-color: #666666;
        }

        td {
            background-color: #e8e8e8;
        }

        .spacer {
            margin: 10px;
        }

        .spacer-lg {
            margin: 40px;
        }

        .indent1 {
            padding: 4px 20px;
        }

        .indent2 {
            padding: 4px 40px;
        }

        .risk-3 {
            background-color: red;
            color: #FFF;
        }

        .risk-2 {
            background-color: orange;
            color: #FFF;
        }

        .risk-1 {
            background-color: yellow;
            color: #000;
        }

        .risk-0 {
            background-color: blue;
            color: #FFF;
        }

        .risk--1 {
            background-color: green;
            color: #FFF;
        }

        .summary {
            width: 45%;
        }

        .summary th {
            color: #FFF;
        }

        .alerts {
            width: 75%;
        }

        .alerts th {
            color: #FFF;
        }

        .results {
            width: 100%;
        }

        .results th {
            text-align: left;
        }

        .left-header {
            display: inline-block;
        }
        </style>
        </head>
    '''
    html_str +=f'''
        <body>
            <h1>
                <!-- The ZAP Logo -->
                <img
                    src="data:image/png;base64,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"
                    alt="" />
                ZAP Scanning Report
            </h1>
            <p />
            

            <h2>
                Sites: {url}
            </h2>

            <h3>
                Generated on {datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S")} UTC
            </h3>

            
                <h3 class="left-header">Summary of Alerts</h3>
                <table class="summary">
                    <tr>
                        <th width="45%"
                            height="24">Risk Level</th>
                        <th width="55%"
                            align="center">Number of Alerts</th>
                    </tr>
                    <tr>
                        <td class="risk-3">
                            <div>High</div>
                        </td>
                        <td align="center">
                            <div>{risk_levels['High']['count']}</div>
                        </td>
                    </tr>
                    <tr>
                        <td class="risk-2">
                            <div>Medium</div>
                        </td>
                        <td align="center">
                            <div>{risk_levels['Medium']['count']}</div>
                        </td>
                    </tr>
                    <tr>
                        <td class="risk-1">
                            <div>Low</div>
                        </td>
                        <td align="center">
                            <div>{risk_levels['Low']['count']}</div>
                        </td>
                    </tr>
                    <tr>
                        <td class="risk-0">
                            <div>Informational</div>
                        </td>
                        <td align="center">
                            <div>{risk_levels['Informational']['count']}</div>
                        </td>
                    </tr>
                    <tr>
                        <td class="risk--1">
                            <div>				False Positives:</div>
                        </td>
                        <td align="center">
                            <div>{risk_levels['False Positives:']['count']}</div>
                        </td>
                    </tr>
                </table>
                <div class="spacer-lg"></div>
            

            
                <h3>Alerts</h3>
                <table class="alerts">
                    <tr>
                        <th width="60%" height="24">Name</th>
                        <th width="20%"
                            align="center">Risk Level</th>
                        <th width="20%"
                            align="center">Number of Instances</th>
                    </tr>
                    {alerts_html}
                    
                </table>
                <div class="spacer-lg"></div>
            

                <h3>Alert Detail</h3>
                {alert_details_html}
        </body>
        </html>

    '''
    return html_str