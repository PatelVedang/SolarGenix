from time import sleep
from django.core.mail import send_mail
from celery import shared_task
import subprocess
import re
import time
from colored import fg, bg, attr
from .models import Machine
from celery.exceptions import SoftTimeLimitExceeded

@shared_task(time_limit=40)
def scan(ip, client):
    start_time = time.time()
    output = ""
    machine = Machine.objects.filter(ip=ip, client=client)

    try:
        # output = subprocess.check_output(f"nmap -Pn -sV {ip} -p23,3389,445", shell=True, timeout=30).decode('utf-8')
        output = subprocess.check_output(f"nmap -Pn -sV {ip}", shell=True, timeout=30).decode('utf-8')
    except Exception as e:
        print("====>>>>>>>>       ", "Background Thread Terminated", "       <<<<<<<<====")
        machine.update(result=output, scanned=False, bg_task_status=True)
        return False

    port_search_regex = '(?P<port>\d{1,4}/tcp)\s+(?P<state>(filtered|open|closed))'
    ignore_state_regex = "All 1000 scanned ports on \d{1,3}.\d{1,3}.\d{1,3}.\d{1,3} are in ignored states."
    ports = list(re.finditer(port_search_regex, output))
    
    # If not found any open ports
    if re.search(ignore_state_regex, output):
        machine.update(result=output, scanned=True, bg_task_status=True)
    
    # If ports found in given time
    elif ports:
        machine.update(result=output, scanned=True, bg_task_status=True)
    end_time = time.time()
    return True
    