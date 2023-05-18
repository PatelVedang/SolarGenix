from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
import logging
logger = logging.getLogger('django')

def send_email(subject, body, sender, recipients, fail_silently, otp = ""):
    logger.info(f"***************** SEND MAIL  *****************")
    logger.info(f"Recipients: {recipients}")
    try:
        if otp:
            html_message = render_to_string('reset-password.html', {'otp': otp})
            sent = send_mail(
                subject=subject,
                message=body,
                from_email=sender,
                recipient_list=recipients,
                fail_silently=fail_silently,
                html_message=html_message
            )
        else:
            sent = send_mail(
                subject=subject,
                message=body,
                from_email=sender,
                recipient_list=recipients,
                fail_silently=fail_silently
            )
        logger.info(f"response {sent}")
        logger.info(f"Please check your inbox.")
    except Exception as e:
        logger.error(str(e))
    
    return True