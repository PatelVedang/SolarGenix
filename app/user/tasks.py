from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

@shared_task
def send_email(subject, body, sender, recipients, fail_silently, otp = ""):
    print(f"***************** SEND MAIL  *****************")
    print(f"Recipients: {recipients}")
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
        print("response", sent)
        print(f"Please check your inbox.")
    except Exception as e:
        print(f"Error: {str(e)}")