from celery import Celery
import subprocess
import re
import time
from .models import Target, TargetLog
import platform
# from utils.message import send
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import json
import requests
from celery import shared_task
import logging
logger = logging.getLogger('django')
from django.db.models import Q
from django.conf import settings
from datetime import datetime
import threading
from tldextract import extract

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
    # thread = threading.Thread(target=send_message, args=(id, token, order_id, batch_scan))
    # thread.start()

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
    if (tool_cmd.find("<ip>")>=0) or (tool_cmd.find("<IP>")>=0):
        tool_cmd = tool_cmd.replace("<ip>",ip).replace("<IP>",ip)
    else:
        tool_cmd += f' {ip}'
    
    if target[0].status >= 1:
        try:
            logger.info(f"====>>>>>>>>       \nScanning began for IP:{ip} with id:{id}\n       <<<<<<<<====")
            target.update(status = 2)
            start_time = datetime.utcnow()
            if platform.uname().system == 'Windows':
                # output = subprocess.check_output(f"{tool_cmd} {ip}", shell=False, timeout=time_limit).decode('utf-8')
                output = subprocess.run(f"{tool_cmd}", shell=False, capture_output=True, timeout=time_limit)
            else:
                # output = subprocess.check_output(f"{tool_cmd} {ip}", shell=True, timeout=time_limit).decode('utf-8')
                output = subprocess.run(f"{tool_cmd}", shell=True, capture_output=True, timeout=time_limit)
            if tool_cmd.lower().find("uniscan"):
                subprocess.run(f"echo {pwd}| sudo -S rm -f /usr/share/uniscan/report/{ip}.html",shell=True, capture_output=True)
            
            if output.stderr.decode('utf-8') and not output.stdout.decode('utf-8'):
                logger.info(f"====>>>>>>>>       \nBackground thread for ip:{ip} with id:{id} has been terminated due to tool issue.\n       <<<<<<<<====")
                update_target_and_add_log(target=target, output=output.stderr.decode('utf-8'), id=id, status=3, action=3, scan_time = get_scan_time(start_time=start_time))
                return False
            
            output=output.stdout.decode('utf-8')
        except Exception as e:
            if e.output:
                error = f'\n{e.output.decode("utf-8")}{str(e)}'
            else:
                error = f'{str(e)}'

            logger.info(f"====>>>>>>>>       \nBackground thread for ip:{ip} with id:{id} has been terminated\n       <<<<<<<<====")
            update_target_and_add_log(target=target, output=str(error), id=id, status=3, action=3, scan_time = get_scan_time(start_time=start_time))
            return False

        update_target_and_add_log(target=target, output=output, id=id, status=4, action=4, scan_time = get_scan_time(start_time=start_time))
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
        # if not Target.objects.filter(order_id=order_id).exclude(id=id).filter(status__gte=1).count():
        # if not Target.objects.filter(order_id=order_id).exclude(id=id).filter(status__in=[2]).count():
            # Target.objects.filter(id=id).update(status=1)
        logger.info(f"====>>>>>>>>       \nWebsocket API trigger for order_id:{order_id}\n       <<<<<<<<====")
        response = requests.get(f'http://localhost:8000/api/sendMessage/?order={order_id}', headers={'Authorization': token})
    else:
        logger.info(f"====>>>>>>>>       \nWebsocket API trigger for target id:{id}\n       <<<<<<<<====")
        response = requests.get(f'http://localhost:8000/api/sendMessage/?id={id}', headers={'Authorization': token})

    return True
