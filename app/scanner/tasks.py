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
    result = ""
    # output = subprocess.getoutput(f'nmap -Pn -sV {self.IPAddress} -p23,3389,445')
    output = subprocess.getoutput(f'nmap -Pn -sV {ip} --host-timeout 30s')
    search_regex = '(?P<port>\d{1,4}/tcp)\s+(?P<state>(filtered|open|closed))'
    header_regex = 'PORT\s+STATE'
    ports = list(re.finditer(search_regex, output))
    headers = re.search(header_regex, output)
    machine = Machine.objects.filter(ip=ip, client=client)
    
    # If Scan thread is Terminated after 30s
    if not headers:
        print("====>>>>>>>>       ", "Background Thread Terminated", "       <<<<<<<<====")
        machine.update(result=output, scanned=False, bg_task_status=True)
        end_time = time.time()
        result += f"{fg('blue_3b')}Scan completed in {round(end_time-start_time)}s{attr('reset')}\n\n{fg('white')}{attr('bold')}Vulnerability Threat Level{attr('reset')}"
        return result
    
    machine.update(result=output, scanned=True, bg_task_status=True)
    end_time = time.time()
    result += f"{fg('blue_3b')}Scan completed in {round(end_time-start_time)}s{attr('reset')}\n\n{fg('white')}{attr('bold')}Vulnerability Threat Level{attr('reset')}"
    return result
    