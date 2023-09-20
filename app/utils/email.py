from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
import traceback
import logging
logger = logging.getLogger('django')

# def send_email(subject, body, sender, recipients, fail_silently, otp = ""):
def send_email(**kwargs):
    subject=kwargs.get('subject')
    body=kwargs.get('body')
    sender=kwargs.get('sender')
    recipients=kwargs.get('recipients')
    fail_silently=kwargs.get('fail_silently')
    otp=kwargs.get('otp')
    link=kwargs.get('link')
    email=kwargs.get('email')
    allow_html=kwargs.get('allow_html')

    
    logger.info(f"***************** SEND MAIL  *****************")
    logger.info(f"Recipients: {recipients}")
    try:
        # Send email with html content
        if allow_html:    
            if otp:
                html_message = render_to_string('reset-password.html', {'otp': otp})
            elif link:
                html_message = render_to_string('verify-user.html', kwargs)
            elif kwargs.get('admin_user_confimartion'):
                html_message = render_to_string('admin-confirmation.html', kwargs)
            elif kwargs.get('end_user_confimartion'):
                html_message = render_to_string('user-confirmation.html', kwargs)
            elif kwargs.get('account_activation'):
                html_message = render_to_string('account-activation.html', kwargs)

            sent = send_mail(
                subject=subject,
                message=body,
                from_email=sender,
                recipient_list=recipients,
                fail_silently=fail_silently,
                html_message=html_message
            )
        else:
            # Send plain email
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
        traceback.print_exc()
        logger.error(str(e))
    
    return True