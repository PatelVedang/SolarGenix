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


def update_target_and_add_log(**kwargs):
    if kwargs.get('output'):
        kwargs.get('target').update(raw_result=kwargs.get('output'), status=kwargs.get('status'))
    else:
        kwargs.get('target').update(status=kwargs.get('status'))
    TargetLog.objects.create(target=Target(kwargs.get('id')), action=kwargs.get('action'))

c = Celery('proj')
@c.task
def scan(id, time_limit, token, order_id, batch_scan):
    """
    It takes the id of the target, the time limit and the token as parameters and then sends a message
    to the user with the id and token. Then it gets the target with the given id and gets the ip of the
    target. Then it logs the ip and id of the target. Then it starts the timer. Then it creates an empty
    string for the output. Then it gets the command of the tool and the time limit of the tool. Then it
    checks if the status of the target is 0. If it is, it updates the status of the target to 1 and
    creates a log for the target with the action 2. Then it checks if the status of the target is
    greater than or equal to 1. If it is, it tries to scan the target. If it can't scan the target, it
    logs the error and updates the status of the target to 3 and creates a log for the target with the
    action 3. If it can scan the target, it gets
    
    :param id: The id of the target to be scanned
    :param time_limit: The time limit for the scan
    :param token: The token of the user who added the target
    :return: the result of the scan.
    """
    send_message.delay(id, token, order_id, batch_scan)
    target = Target.objects.filter(id=id)
    ip = target[0].ip
    logger.info(f"====>>>>>>>>       \nIP:{ip} with id:{id} added to queue\n       <<<<<<<<====")
    start_time = time.time()
    output = ""
    tool_cmd = target[0].tool.tool_cmd
    time_limit = target[0].tool.time_limit
    pwd = settings.SUDO_PWD
    # if tool is uniscan then we have to add sudo access
    if tool_cmd.lower().find("uniscan") >=0:
        tool_cmd = f'echo {pwd} | sudo -S {tool_cmd}'
    # if record is just created
    if target[0].status == 0:
        # target.update(status=1)
        # TargetLog.objects.create(target=Target(id), action=2)
        update_target_and_add_log(target=target, id=id, status=1, action=2)

    # if record is credated and scan was already did
    if target[0].status >= 1:
        try:
            logger.info(f"====>>>>>>>>       \nScanning began for IP:{ip} with id:{id}\n       <<<<<<<<====")
            target.update(status = 2)
            if platform.uname().system == 'Windows':
                # output = subprocess.check_output(f"{tool_cmd} {ip}", shell=False, timeout=time_limit).decode('utf-8')
                output = subprocess.run(f"{tool_cmd} {ip}", shell=False, capture_output=True, timeout=time_limit)
            else:
                # output = subprocess.check_output(f"{tool_cmd} {ip}", shell=True, timeout=time_limit).decode('utf-8')
                output = subprocess.run(f"{tool_cmd} {ip}", shell=True, capture_output=True, timeout=time_limit)

            if tool_cmd.lower().find("uniscan"):
                subprocess.run(f"echo {pwd}| sudo -S rm -f /usr/share/uniscan/report/{ip}.html",shell=True, capture_output=True)
            
            if output.stderr.decode('utf-8'):
                logger.info(f"====>>>>>>>>       \nBackground thread for ip:{ip} with id:{id} has been terminated due to tool issue.\n       <<<<<<<<====")
                update_target_and_add_log(target=target, output=output.stderr.decode('utf-8'), id=id, status=3, action=3)
                return False
            
            output=output.stdout.decode('utf-8')
        except Exception as e:
            if e.output:
                error = f'\n{e.output.decode("utf-8")}{str(e)}'
            else:
                error = f'{str(e)}'

            logger.info(f"====>>>>>>>>       \nBackground thread for ip:{ip} with id:{id} has been terminated\n       <<<<<<<<====")
            update_target_and_add_log(target=target, output=str(error), id=id, status=3, action=3)
            return False

        port_search_regex = '(?P<port>\d{1,4}/tcp)\s+(?P<state>(filtered|open|closed))'
        ignore_state_regex = "All 1000 scanned ports on \d{1,3}.\d{1,3}.\d{1,3}.\d{1,3} are in ignored states."
        filtered_state_regex = "All 1000 scanned ports on \d{1,3}.\d{1,3}.\d{1,3}.\d{1,3} are filtered"
        ports = list(re.finditer(port_search_regex, output))
        
        # If not found any open ports
        if (re.search(ignore_state_regex, output) or re.search(filtered_state_regex, output)):
            logger.info(f"====>>>>>>>>       \nIP:{ip} with id:{id} has no open ports.\n       <<<<<<<<====")
            update_target_and_add_log(target=target, output=output, id=id, status=4, action=4)
        
        # If ports found in given time
        elif ports:
            logger.info(f"====>>>>>>>>       \nFound open ports with IP:{ip} with id:{id}.\n       <<<<<<<<====")
            update_target_and_add_log(target=target, output=output, id=id, status=4, action=4)
        else:
            logger.info(f"====>>>>>>>>       \nIP:{ip} with id:{id} is not match any condition.\n       <<<<<<<<====")
            update_target_and_add_log(target=target, output=output, id=id, status=4, action=4)

        end_time = time.time()
        return True
    else:
        return False

@shared_task
def send_message(id, token, order_id, batch_scan):
    """
    This function sends a request to the API to send a message to the target user
    
    :param id: The id of the target user
    :param token: The token you get from the login API
    """
    if batch_scan:
        # if not Target.objects.filter(order_id=order_id).exclude(id=id).filter(status__gte=1).count():
        if not Target.objects.filter(order_id=order_id).exclude(id=id).filter(status__in=[1,2]).count():
            # Target.objects.filter(id=id).update(status=1)
            logger.info(f"====>>>>>>>>       \nWebsocket API trigger for order_id:{order_id}\n       <<<<<<<<====")
            response = requests.get(f'http://localhost:8000/api/sendMessage/?order={order_id}', headers={'Authorization': token})
    else:
        logger.info(f"====>>>>>>>>       \nWebsocket API trigger for target id:{id}\n       <<<<<<<<====")
        response = requests.get(f'http://localhost:8000/api/sendMessage/?id={id}', headers={'Authorization': token})
