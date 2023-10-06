from django.conf import settings
import uuid
from scanner.models import Target, Order
import os
import logging
from datetime import datetime
from tldextract import extract
import socket
from .report_lab_doc import generate_doc
logger = logging.getLogger('django')
from .handlers.nmap_handler import NMAP
nmap = NMAP()
from .handlers.sslyze_handler import SSLYSE
sslyze = SSLYSE()
from .handlers.nikto_handler import NIKTO
nikto = NIKTO()
from .handlers.curl_handler import CURL
curl = CURL()
from .handlers.default_handler import DEFAULT
default = DEFAULT()
from .handlers.owasp_zap_handler import OWASP
owasp = OWASP()
from .handlers.common_handler import Templates
t = Templates()


class PDF:
    PDF_PATH = f'{settings.MEDIA_ROOT}pdf'
    result = ""
    handlers = {
        'nmap': nmap.main,
        'sslyze': sslyze.main,
        'nikto': nikto.main,
        'curl': curl.main,
        'owasp_zap': owasp.main,
        'isaix_owasp': owasp.main,
        'active_owasp': owasp.main,
        'default': default.default_handler
    }

    def make_path(self, target_path):
        """
        It takes a path, splits it into a list, and then iterates over the list, creating a directory
        for each item in the list
        
        :param target_path: The path to the directory you want to create
        """
        sub_path = target_path.replace(str(settings.BASE_DIR), '')
        sub_path_content = sub_path.split("/")
        for index in range(len(sub_path_content)):
            path = f'{settings.BASE_DIR}{"/".join(sub_path_content[:index+1])}'
            if not os.path.exists(path):
                os.mkdir(path)
            self.path = path

    def delete_existing_file(self, file_path):
        """
        If the file exists, delete it
        
        :param file_path: The path to the file you want to delete
        """
        if os.path.exists(f'{file_path}'):
            os.remove(f'{file_path}')

    def generate(self, role, user_id, order_id, targets_ids=[], generate_pdf=True, generate_order_pdf=False, re_generate = False):
        order_obj = Order.objects.get(id=order_id)
        target_obj = None
        alert_objs = {}
        risk_levels = {
            'critical': 0,
            'high': 0,
            'medium':0,
            'low':0,
            'informational':0,
            'false-positive':0
        }
        ip = ""
        # start = datetime.utcnow()
        for target_id in targets_ids:
            target_obj = Target.objects.get(id=target_id)
            ip = target_obj.ip
            if self.handlers.get(target_obj.tool.tool_cmd.split(" ")[0]):
                handler_result = self.handlers[target_obj.tool.tool_cmd.split(" ")[0]](target_obj, re_generate)
            else:
                handler_result = self.handlers['default'](target_obj, re_generate)
            
            try:
                # New flow(If handler_result is json)
                if handler_result:
                    for error,value in handler_result.items():
                        complexity = value.get('complexity')
                        html_data = t.templates(**value)
                        alert_objs = {**alert_objs, **
                            {
                                f'{error}_{complexity}': {**value,**{'html_data': html_data}}
                            }
                        }
                        if risk_levels.get(complexity.lower()) == 0 or risk_levels.get(complexity.lower()):
                            risk_levels[complexity.lower()] += 1
            except:
                import traceback
                traceback.print_exc()
                pass
        # print(f"entire process take arround {(datetime.utcnow()-start).total_seconds()} Seconds")
        alert_objs = dict(sorted(alert_objs.items(), key=lambda x: x[1].get('alert_order')))
        
        if generate_pdf:

            new_pdf_name = f'{str(uuid.uuid4())}.pdf'
            
            if generate_order_pdf:
                abs_path = f'{self.PDF_PATH}/{user_id}/{order_id}'
                self.make_path(f'{abs_path}')
                file_path = f'{self.path}/{new_pdf_name}'
                file_path_for_db = file_path.replace(str(settings.MEDIA_ROOT), '')
                if order_obj.pdf_path:
                    self.delete_existing_file(f'{settings.MEDIA_ROOT}/{order_obj.pdf_path}')
                Order.objects.filter(id=order_id).update(pdf_path=file_path_for_db)
            else:
                abs_path = f'{self.PDF_PATH}/{user_id}/{order_id}/{target_id}'
                self.make_path(f'{abs_path}')
                file_path = f'{self.path}/{new_pdf_name}'
                file_path_for_db = file_path.replace(str(settings.MEDIA_ROOT), '')
                if target_obj.pdf_path:
                    self.delete_existing_file(f'{settings.MEDIA_ROOT}{target_obj.pdf_path}')
                Target.objects.filter(id=target_id).update(pdf_path=file_path_for_db)
      
            origin = ".".join(list(extract(ip))).strip(".")
            ip = socket.gethostbyname(origin)
            generate_doc(role, cname='ISAIX',
                scan_date=order_obj.created_at.strftime("%b %d %Y"),
                vulnerabilities=alert_objs,
                user_name = f"{order_obj.client.first_name} {order_obj.client.last_name}".upper(),
                user_company = order_obj.client.user_company,
                user_company_address = order_obj.client.user_address,
                profile_image= order_obj.client.profile_image,
                risk_levels=risk_levels,
                output_path=file_path,
                multiple_ip=True,
                hosts=[[ip, origin, list(risk_levels.values())[:-1]]]
            )
            file_url = f"{settings.PDF_DOWNLOAD_ORIGIN}/media/{file_path_for_db}"
            return file_path, new_pdf_name, file_url
        else:
            logger.info(f'HTML Genrated successfully by user id {user_id} for target id {target_id}')
            return ""


