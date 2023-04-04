from django.conf import settings
import pdfkit
import uuid
from scanner.models import Target, Order
import os
import logging
logger = logging.getLogger('django')
from .handlers.nmap_hanlder import NMAP
nmap = NMAP()
from .handlers.sslyze_handler import SSLYSE
sslyze = SSLYSE()
from .handlers.nikto_handler import NIKTO
nikto = NIKTO()
from .handlers.default_handler import DEFAULT
default = DEFAULT()


class PDF:
    PDF_PATH = f'{settings.MEDIA_ROOT}pdf'
    result = ""
    handlers = {
        'nmap': nmap.nmap_handler,
        # 'nmap-poodle': nmap.nmap_poodle_handler,
        # 'nmap-vuln': nmap.nmap_vuln_handler,
        # 'nmap-vulners': nmap.nmap_vulners_handler,
        'sslyze': sslyze.sslyze_handler,
        'nikto': nikto.nikto_handler,
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
        It takes a list of target ids, and generates a pdf for each target id. 
        
        :param user_id: The user id of the user who is generating the report
        :param order_id: The id of the order you want to generate the PDF for
        :param targets_ids: The list of target ids for which the pdf is to be generated
        :param generate_pdf: If True, it will generate a PDF file. If False, it will return the HTML
        string, defaults to True (optional)
        :param generate_order_pdf: If True, the PDF will be generated for the entire order. If False,
        the PDF will be generated for the target, defaults to False (optional)
        :param re_generate: If you want to re-generate the pdf, set this to True, defaults to False
        (optional)
        """
        self.result = ""
        order_obj = Order.objects.get(id=order_id)
        target_obj = None
        
        for target_id in targets_ids:
            target_obj = Target.objects.get(id=target_id)
            if self.handlers.get(target_obj.tool.tool_cmd.split(" ")[0]):
                self.result += self.handlers[target_obj.tool.tool_cmd.split(" ")[0]](target_obj, re_generate)
            else:
                self.result += self.handlers['default'](target_obj, re_generate)
        
        # Base html
        html_data = f"""<!DOCTYPE html>
        <html lang="en">
        <head>
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.6.2/dist/css/bootstrap.min.css"
                integrity="sha384-xOolHFLEh07PJGoPkLv1IbcEPTNtaed2xpHsD9ESMhqIYd0nLMwNLD69Npy4HI+N" crossorigin="anonymous">
        </head>

        <body>
            <div class="container-fluid">   
                <div class="row border border-1 border-dark">
                    {self.result}
                </div>
            </div>
        </body>

        </html>"""

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


