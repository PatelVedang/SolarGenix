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
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

c = Celery('proj')
@c.task
def scan(id, time_limit, token):
    send_message.delay(id, token)
    """
    It takes the id of the target object, and then it runs the tool command on the ip of the target
    object
    
    :param id: The id of the target to be scanned
    :return: The return value is a boolean value.
    """
    target = Target.objects.filter(id=id)
    ip = target[0].ip
    logger.info(f"====>>>>>>>>       \nIP:{ip} with id:{id} added to queue\n       <<<<<<<<====")
    start_time = time.time()
    output = ""
    tool_cmd = target[0].tool.tool_cmd
    time_limit = target[0].tool.time_limit
    if target[0].status == 0:
        target.update(status=1)
        TargetLog.objects.create(target=Target(id), action=2)
    if target[0].status >= 1:
        try:
            logger.info(f"====>>>>>>>>       \nScanning began for IP:{ip} with id:{id}\n       <<<<<<<<====")
            target.update(status = 2)
            if platform.uname().system == 'Windows':
                output = subprocess.check_output(f"{tool_cmd} {ip}", shell=False, timeout=time_limit).decode('utf-8')
            else:
                output = subprocess.check_output(f"{tool_cmd} {ip}", shell=True, timeout=time_limit).decode('utf-8')
        except Exception as e:
            logger.info(f"====>>>>>>>>       \nBackground thread for ip:{ip} with id:{id} has been terminated\n       <<<<<<<<====")
            target.update(result=str(e), status=3)
            TargetLog.objects.create(target=Target(id), action=3)
            return False

        port_search_regex = '(?P<port>\d{1,4}/tcp)\s+(?P<state>(filtered|open|closed))'
        ignore_state_regex = "All 1000 scanned ports on \d{1,3}.\d{1,3}.\d{1,3}.\d{1,3} are in ignored states."
        filtered_state_regex = "All 1000 scanned ports on \d{1,3}.\d{1,3}.\d{1,3}.\d{1,3} are filtered"
        ports = list(re.finditer(port_search_regex, output))
        
        # If not found any open ports
        if (re.search(ignore_state_regex, output) or re.search(filtered_state_regex, output)):
            logger.info(f"====>>>>>>>>       \nIP:{ip} with id:{id} has no open ports.\n       <<<<<<<<====")
            target.update(result=output, status=4)
            TargetLog.objects.create(target=Target(id), action=4)
        
        # If ports found in given time
        elif ports:
            logger.info(f"====>>>>>>>>       \nFound open ports with IP:{ip} with id:{id}.\n       <<<<<<<<====")
            target.update(result=output, status=4)
            TargetLog.objects.create(target=Target(id), action=4)
        else:
            logger.info(f"====>>>>>>>>       \nIP:{ip} with id:{id} is not match any condition.\n       <<<<<<<<====")
            target.update(result=output, status=4)
            TargetLog.objects.create(target=Target(id), action=4)

        end_time = time.time()
        return True
    else:
        return False

@shared_task
def send_message(id, token):
    logger.info(f"====>>>>>>>>       \nWebsocket API trigger for target id:{id}\n       <<<<<<<<====")
    response = requests.get(f'http://localhost:8000/api/sendMessage/?id={id}', headers={'Authorization': token})