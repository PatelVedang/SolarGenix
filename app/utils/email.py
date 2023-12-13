from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import traceback
import logging
logger = logging.getLogger('django')

def send_email(**kwargs):
    subject=kwargs.get('subject', '')
    body=kwargs.get('body', '')
    sender=kwargs.get('sender')
    recipients=kwargs.get('recipients', [])
    bcc=kwargs.get('bcc', [])
    attachments=kwargs.get('attachments', [])
    html_template=kwargs.get('html_template', '')
    html_string=kwargs.get('html_string', '')
    print(recipients,"=>>>>>>>Recepients")
    
    logger.info(f"***************** SEND MAIL  *****************")
    logger.info(f"Recipients: {recipients}")
    try:
        email = EmailMessage(subject, strip_tags(body), sender, recipients, bcc=bcc)
         # Attachments
        if attachments:
            for attachment in attachments:
                with open(attachment['path'], 'rb') as file:
                    email.attach(attachment['name'], file.read(), attachment['mime-type'])    # HTML content in the body

        # # HTML content in the body
        if html_template:
            html_message = render_to_string(html_template, kwargs)
            email.content_subtype = "html"
            email.body = html_message
        
        if html_string:
            html_message = html_string
            email.content_subtype = "html"
            email.body = html_message

        # Send the email
        email.send()
        
        # logger.info(f"response {email}")
        # logger.info(f"Please check your inbox.")
        print(f"response {email}")
        print(f"Please check your inbox.")
    except Exception as e:
        print(e,"=>>>>>>>>>>>>Error")
        traceback.print_exc()
        logger.error(str(e))
    
    return True