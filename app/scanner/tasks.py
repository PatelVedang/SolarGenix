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
def scan(ip):
    start_time = time.time()
    result = ""
    # output = subprocess.getoutput(f'nmap -Pn -sV {self.IPAddress} -p23,3389,445')
    output = subprocess.getoutput(f'nmap -Pn -sV {ip} --host-timeout 30s')
    search_regex = '(?P<port>\d{1,4}/tcp)\s+(?P<state>(filtered|open|closed))'
    header_regex = 'PORT\s+STATE'
    ports = list(re.finditer(search_regex, output))
    headers = re.search(header_regex, output)
    machine = Machine.objects.filter(ip=ip)
    
    # If Scan thread is Terminated after 30s
    if not headers:
        print("====>>>>>>>>       ", "Background Thread Terminated", "       <<<<<<<<====")
        if not machine.exists():
            data = Machine.objects.create(ip=ip,result=output, scanned=False)    
        end_time = time.time()
        result += f"{fg('blue_3b')}Scan completed in {round(end_time-start_time)}s{attr('reset')}\n\n{fg('white')}{attr('bold')}Vulnerability Threat Level{attr('reset')}"
        return result
    
    if ports:
        # smb = check_port_status(result, ports, 445,log=f"\n\t{bg('red')} high {fg('white')}{attr('reset')}{fg('dark_orange')} SBM Ports are Open over TCP.{attr('reset')}\n")
        # telnet = check_port_status(result, ports, 23,log = f"\n\t{bg('purple_4b')} critical {fg('white')}{attr('reset')}{fg('dark_orange')} FTP Service detected.{attr('reset')}\n")
        # rdp = check_port_status(result, ports, 3389, log = f"\n\t{bg('sandy_brown')} medium {fg('white')}{attr('reset')}{fg('dark_orange')} RDP Server Detected over TCP.{attr('reset')}\n")
        if machine.exists():
            
            data = machine.update(result=output, scanned=True)
        else:
            data = Machine.objects.create(ip=ip, result=output, scanned=True)
    else:
        if machine.exists():
            data = machine.update(result=output, scanned=True)
        else:
            data = Machine.objects.create(ip=ip, result=output, scanned=True)
    end_time = time.time()
    result += f"{fg('blue_3b')}Scan completed in {round(end_time-start_time)}s{attr('reset')}\n\n{fg('white')}{attr('bold')}Vulnerability Threat Level{attr('reset')}"
    return result 

    
# def check_port_status(result, ports, port,log):
#     port_running = 0
#     try:
#         for port_text in ports:
#             port_obj = port_text.groupdict()
#             if int(port_obj['port'].split('/')[0]) == port:
#                 if port_obj:
#                     if port_obj.get('state') == 'open':
#                         result += log
#                         port_running = 1
#                     else:
#                         port_running = 0
#                 else:
#                     port_running = 0
#                 return port_running
#             else:
#                 continue
#     except Exception as e:
#         print(e,"Exception Found")
#         return port_running
#     return port_running
    