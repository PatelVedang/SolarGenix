from celery import Celery, current_task
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
import traceback
import asyncio
import aiohttp
from utils.owasp.scan import Scanner
owasp = Scanner()
from datetime import datetime

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
def scan(id, time_limit, token, order_id, user_id, batch_scan):
    thread = threading.Thread(target=send_message, args=(id, token, order_id, batch_scan))
    thread.start()

    py_tools={
        'owasp_zap':OWASP_ZAP_spider_scan_v3,
        'isaix_owasp': custom_OWASP_ZAP_scan
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

                    # # Set the timeout signal and handler
                    # signal.signal(signal.SIGALRM, timeout_handler)
                    # # signal.signal(signal.SIGALRM, lambda signum, frame: timeout_handler(signum, frame, target[0].id))
                    # signal.alarm(time_limit)
                    
                    # Calling the python tool(ex. owasp)
                    output = py_tools.get(tool_cmd)(ip, order_id, user_id, time_limit)
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
    try:
        if batch_scan:
            if not Target.objects.filter(order_id=order_id).exclude(id=id).filter(status__in=[2]).count():
                logger.info(f"====>>>>>>>>       \nWebsocket API trigger for order_id:{order_id}\n       <<<<<<<<====")
                response = requests.get(f'{settings.LOCAL_API_URL}/api/sendMessage/?order={order_id}', headers={'Authorization': token})
        else:
            logger.info(f"====>>>>>>>>       \nWebsocket API trigger for target id:{id}\n       <<<<<<<<====")
            response = requests.get(f'{settings.LOCAL_API_URL}/api/sendMessage/?id={id}', headers={'Authorization': token})
    except Exception as e:
        return True
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

def OWASP_ZAP_spider_scan_v3(url, order_id, user_id, time_limit):
    # To store json as a scan result

    # Set the timeout signal and handler
    signal.signal(signal.SIGALRM, timeout_handler, )
    # signal.signal(signal.SIGALRM, lambda signum, frame: timeout_handler(signum, frame, target[0].id))
    signal.alarm(time_limit)

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

    return json.dumps({'alerts': alerts})

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

def custom_OWASP_ZAP_scan(url, order_id, user_id, time_limit):
    domain = ".".join(list(extract(url))).strip(".")
    http_url = f"http://{domain}"
    https_url = f"https://{domain}"
    if not ('http://' in url or 'https://' in url):
        url = http_url
    # try:
    return owasp.process_data(url, order_id, user_id, time_limit)
    # except Exception as e:
    #     pass