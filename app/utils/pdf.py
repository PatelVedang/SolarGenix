from django.conf import settings
import pdfkit
import uuid
from scanner.models import Target, Order
import os
from bs4 import BeautifulSoup
import logging
from datetime import datetime
from tldextract import extract
import json
logger = logging.getLogger('django')
from .handlers.nmap_hanlder import NMAP
nmap = NMAP()
from .handlers.sslyze_handler import SSLYSE
sslyze = SSLYSE()
from .handlers.nikto_handler import NIKTO
nikto = NIKTO()
from .handlers.curl_handler import CURL
curl = CURL()
from .handlers.default_handler import DEFAULT
default = DEFAULT()
from .handlers.owasp_zap_hanlder import OWASP
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

    def generate(self, user_id, order_id, targets_ids=[], generate_pdf=True, generate_order_pdf=False, re_generate = False):
        """
        This function generates a report in HTML or PDF format for a given order and target, including a
        summary of alerts and their risk levels.
        
        :param user_id: The ID of the user who is generating the report
        :param order_id: The ID of the order object that contains the targets to be scanned
        :param targets_ids: targets_ids is a list of target ids for which the report needs to be
        generated. The function generates a report for each target in the list. If the list is empty,
        the function does not generate any report
        :param generate_pdf: A boolean parameter that determines whether to generate a PDF file or not.
        If True, a PDF file will be generated, otherwise only an HTML string will be returned, defaults
        to True (optional)
        :param generate_order_pdf: The parameter `generate_order_pdf` is a boolean flag that indicates
        whether to generate a PDF report for the entire order or not. If set to `True`, the function
        will generate a single PDF report for the entire order, otherwise, it will generate separate PDF
        reports for each target in the order, defaults to False (optional)
        :param re_generate: The `re_generate` parameter is a boolean flag that indicates whether to
        regenerate the report for a target that has already been scanned before. If set to `True`, the
        report will be regenerated even if a previous report exists for the target. If set to `False`,
        the report will only be generated, defaults to False (optional)
        :return: a tuple containing the file path, new pdf name, and file url. If generate_pdf is False,
        it returns the generated HTML data as a string.
        """
        self.result = ""
        order_obj = Order.objects.get(id=order_id)
        target_obj = None
        alert_objs = {}
        risk_level_objs = {
            'critical': 0,
            'high': 0,
            'medium':0,
            'low':0,
            'informational':0,
            'false-positive':0
        }
        ip = ""
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
                        if risk_level_objs.get(complexity.lower()) == 0 or risk_level_objs.get(complexity.lower()):
                            risk_level_objs[complexity.lower()] += 1
            except:
                import traceback
                traceback.print_exc()
                pass

        alert_objs = dict(sorted(alert_objs.items(), key=lambda x: x[1].get('alert_order')))
        self.result = "\n".join(list(map(lambda x:x.get('html_data',''),alert_objs.values())))
        # Base html
        html_data = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.6.2/dist/css/bootstrap.min.css"
            integrity="sha384-xOolHFLEh07PJGoPkLv1IbcEPTNtaed2xpHsD9ESMhqIYd0nLMwNLD69Npy4HI+N" crossorigin="anonymous">
            <style>
                .medium, .Medium, .MEDIUM{
                    background-color: orange;color:white;
                }
                .high, .High, .HIGH{
                    background-color: #FF0000;color:white;
                }
                .critical, .Critical, .CRITICAL{
                    background-color: #000000;color:#D8D8D8;
                }
                .low, .Low, .LOW{
                    background-color: yellow;
                }
                .info, .Info, .INFO, .Informational, .INFORMATIONAL, .informational {
                    background-color: blue;color:white;
                }
                .False-Positive, .Flase-Positive, .FALSE-POSITIVE{
                    background-color: #00811f;color:white;
                }
                .header{
                    background:#666666; color: white;
                }
                .body{
                    background:#e8e8e8;
                }
            </style>
        </head>"""
        html_data+= f"""
        <body>
            <div class="container-fluid">   
                <div style="text-decoration: none;">
                    <h1>Cyber Appliance</h1><br>
                    <h2>Site: http://{".".join(list(extract(ip))).strip(".")}</h2><br>
                    <h4>Generated on {datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S")} UTC</h4><br>
                </div>
                <div style="text-decoration: none; margin-top: 5%;">
                    <h4>Summary of Alerts</h4>
                </div>
                <div class="row">
                    <div class="col-6 border border-5 border-light">
                        <div class="row">
                            <div class="col-6 border border-5 border-light header">
                                Risk Level 
                            </div>
                            <div class="col-6 border border-5 border-light header">
                                Number of Alerts
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-6 border border-5 border-light critical">
                                Critical
                            </div>
                            <div class="col-6 border border-5 border-light body">
                                {risk_level_objs['critical']}
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-6 border border-5 border-light high">
                                High 
                            </div>
                            <div class="col-6 border border-5 border-light body">
                                {risk_level_objs['high']}
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-6 border border-5 border-light medium">
                                Medium
                            </div>
                            <div class="col-6 border border-5 border-light body">
                                {risk_level_objs['medium']}
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-6 border border-5 border-light low">
                                Low
                            </div>
                            <div class="col-6 border border-5 border-light body">
                                {risk_level_objs['low']}
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-6 border border-5 border-light info">
                                Informational
                            </div>
                            <div class="col-6 border border-5 border-light body">
                                {risk_level_objs['informational']}
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-6 border border-5 border-light False-Positive">
                                False-Positive
                            </div>
                            <div class="col-6 border border-5 border-light body">
                                {risk_level_objs['false-positive']}
                            </div>
                        </div>
                    </div>
                </div>"""
        if len(alert_objs.keys()):
                html_data += """
                <div style="text-decoration: none; margin-top: 5%;">
                    <h4>Alerts</h4>
                </div>
                <div class="row">
                    <div class="col-12 border border-5 border-light">
                        <div class="row">
                            <div class="col-6 border border-5 border-light header">
                                Name 
                            </div>
                            <div class="col-2 border border-5 border-light header">
                                Risk Level
                            </div>
                            <div class="col-2 border border-5 border-light header">
                                Number of instances
                            </div>
                            <div class="col-2 border border-5 border-light header">
                                Alert detection tool
                            </div>
                        </div>
                """
                for key,value in alert_objs.items():
                    html_data += f"""
                        <div class="row">
                            <div class="col-6 border border-5 border-light body">
                                <a href="#{value['alert_ref']}">{key.split("_")[0]}</a>
                            </div>
                            <div class="col-2 border border-5 border-light {value['complexity']}">
                                {value['complexity']}
                            </div>
                            <div class="col-2 border border-5 border-light body">
                                {value['instances']}
                            </div>
                            <div class="col-2 border border-5 border-light body">
                                {value['tool']}
                            </div>
                    
                        </div>"""
                html_data += """
                    </div>
                </div>"""
        
        if self.result:        
            html_data += f"""
            <div style="text-decoration: none; margin-top: 5%;">
                <h4>Alert Detail</h4>
            </div>
            {self.result}
            """
        
        html_data += """
            </div>
        </body>

        </html>
        """
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
      

            logger.info(f'Pdf generated successfully by user id {user_id} for target id {target_id} which is stored in path {file_path}')
            options={
            '--page-size': 'A4',
            'margin-top': '0.5in',
            'margin-right': '0.5in',
            'margin-bottom': '0.5in',
            'margin-left': '0.5in'
            }
            pdfkit.from_string(html_data, output_path=file_path, options=options)
            file_url = f"{settings.PDF_DOWNLOAD_ORIGIN}/media/{file_path_for_db}"
            return file_path, new_pdf_name, file_url
        else:
            logger.info(f'HTML Genrated successfully by user id {user_id} for target id {target_id}')
            return html_data.replace("\n","")


