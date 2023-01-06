from time import sleep
from django.core.mail import send_mail
from celery import shared_task
import subprocess
import re
import time
from colored import fg, bg, attr
from .models import Machine
from celery.exceptions import SoftTimeLimitExceeded

@shared_task(time_limit=40, ignore_result=True)
def scan(id):
    """
    It takes the id of the machine object, and then it runs the tool command on the ip of the machine
    object
    
    :param id: The id of the machine to be scanned
    :return: The return value is a boolean value.
    """
    machine = Machine.objects.filter(id=id)
    ip = machine[0].ip
    print("====>>>>>>>>       ", f"IP:{ip} with id:{id} added to queue", "       <<<<<<<<====")
    start_time = time.time()
    output = ""
    tool_cmd = machine[0].tool.tool_cmd
    if machine[0].status == 0:
        machine.update(status = 1)
    if machine[0].status >= 1:
        try:
            print("====>>>>>>>>       ", f"Scanning began for IP:{ip} with id:{id}", "       <<<<<<<<====")
            machine.update(status = 2)
            output = subprocess.check_output(f"{tool_cmd} {ip}", shell=True, timeout=30).decode('utf-8')
        except Exception as e:
            print("====>>>>>>>>       ", f"Background thread for ip:{ip} with id:{id} has been terminated", "       <<<<<<<<====")
            machine.update(result=str(e), status=3)
            return False

        port_search_regex = '(?P<port>\d{1,4}/tcp)\s+(?P<state>(filtered|open|closed))'
        ignore_state_regex = "All 1000 scanned ports on \d{1,3}.\d{1,3}.\d{1,3}.\d{1,3} are in ignored states."
        ports = list(re.finditer(port_search_regex, output))
        
        # If not found any open ports
        if re.search(ignore_state_regex, output):
            print("====>>>>>>>>       ", f"IP:{ip} with id:{id} has no open ports.", "       <<<<<<<<====")
            machine.update(result=output, status=4)
        
        # If ports found in given time
        elif ports:
            print("====>>>>>>>>       ", f"Found open ports with IP:{ip} with id:{id}.", "       <<<<<<<<====")
            machine.update(result=output, status=4)
        end_time = time.time()
        return True
    else:
        return False