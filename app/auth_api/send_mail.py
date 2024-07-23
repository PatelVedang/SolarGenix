from django.core.mail import EmailMessage
import threading


def send_email(subject, message, email_from, recipient_list):
    email_message = EmailMessage(
        subject,
        message,
        email_from,
        recipient_list,
    )
    email_message.send()


def send_email_async(subject, message, email_from, recipient_list):
    thread = threading.Thread(
        target=send_email,
        kwargs={
            "subject": subject,
            "message": message,
            "email_from": email_from,
            "recipient_list": recipient_list,
        },
    )
    thread.start()