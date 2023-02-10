from django.conf import settings
import pdfkit
import re
import uuid
from scanner.models import Target
import os

class PDF:
    PDF_PATH = f'{settings.MEDIA_ROOT}pdf'
    smb = 445
    telnet = 23
    rdp = 3389
    result = ""

    def make_path(self, target_path):
        sub_path = target_path.replace(str(settings.BASE_DIR), '')
        sub_path_content = sub_path.split("/")
        for index in range(len(sub_path_content)):
            path = f'{settings.BASE_DIR}{"/".join(sub_path_content[:index+1])}'
            if not os.path.exists(path):
                os.mkdir(path)
            self.path = path

    def generate(self, user_id, machine_id, host, generate_pdf=True):
        search_regex = '(?P<port>\d{1,4}/tcp)\s+(?P<state>(filtered|open|closed))'
        machine_obj = Target.objects.get(id=machine_id)
        scan_result = machine_obj.result
        ports = list(re.finditer(search_regex, scan_result))
        self.result = ""
        susceptible_ports = []
        for port_text in ports:
            port_obj = port_text.groupdict()
            port = int(port_obj['port'].split('/')[0])
            state = port_obj['state']
            if port in [self.smb, self.telnet, self.rdp]:
                if state == "open":
                    susceptible_ports.append(port)
                if port == self.smb and state == "open":
                    self.result += '''
                    <div class="ml-5">
                        <span style="color:white;background:red;" class="px-3">high</span><span style="color:#FF8700">&nbsp;SBM Ports are Open over TCP.</span>
                    </div>
                    '''
                if port == self.telnet and state == "open":
                    self.result += '''
                    <div class="ml-5">
                        <span style="color:white;background:#5F00AF;" class="px-3">critical</span><span style="color:#FF8700">&nbsp;FTP Service detected.</span>
                    </div>
                    '''
                if port == self.rdp and state == "open":
                    self.result += '''
                    <div class="ml-5">
                        <span style="color:black;background:#FFAF5F;" class="px-3">medium</span><span style="color:#FF8700">&nbsp;RDP Server Detected over TCP.</span>
                    </div>
                    '''
        
        if susceptible_ports:
            self.result = '''
            <div class="text-white">Vulnerability Threat Level</div>
            ''' + self.result
        else:
            self.result = '''
            <div class="text-white">Not Found Any Vulnerability Threat</div>
            '''
        html_data = f"""<!DOCTYPE html>
        <html lang="en">
        <head>
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.0.0/dist/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
        </head>
        <body>
            <div class="bg-dark">
                <div class="p-5">
                    {self.result}
                </div>
            </div>
        </body>
        </html>"""

        if generate_pdf:
            self.make_path(f'{self.PDF_PATH}/{user_id}/{machine_id}')
                
            if machine_obj.pdf_path:
                if os.path.exists(f'{settings.MEDIA_ROOT}/{machine_obj.pdf_path}'):
                    os.remove(f'{settings.MEDIA_ROOT}/{machine_obj.pdf_path}')

            new_pdf_name = f'{str(uuid.uuid4())}.pdf'
            file_path = f'{self.path}/{new_pdf_name}'
            pdfkit.from_string(html_data, output_path=file_path)
            file_path_for_db = file_path.replace(str(settings.MEDIA_ROOT), '')
            Target.objects.filter(id=machine_id).update(pdf_path=file_path_for_db)
            file_url = f"http://{host}/media/{file_path_for_db}"
            return file_path, new_pdf_name, file_url
        else:
            return html_data.replace("\n","")