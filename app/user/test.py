# from django.core.mail import EmailMessage
from django.conf import settings

# try:
#     email = EmailMessage(
#         subject="Hello1",
#         body="Body goes here1",
#         from_email=settings.BUSINESS_EMAIL,
#         to=["parimal.patel@appaspect.com"],
#         bcc=["parimal.patel@isaix.com"],

#     )
    # with open(f"{settings.MEDIA_ROOT}pdf/1/302/9d5d71f1-cf98-4825-ab6a-3133fa584450.pdf", 'rb') as file:
    #     email.attach("output1.pdf", file.read(), "application/pdf")
    # email.send()

# except Exception as e:
#     print(e,"=>>>Errror")


from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.utils.html import strip_tags

def send_custom_email(subject, message, from_email, recipient_list, bcc_list, attachments=None, html_template=None, context=None):
    # Create EmailMessage instance
    email = EmailMessage(subject, strip_tags(message), from_email, recipient_list, bcc=bcc_list)

    # Attachments
    if attachments:
        for attachment in attachments:
            # email.attach_file(attachment['path'], content_id="output1.pdf")
            # email.attach(filename="output.pdf",content=attachment['path'], mimetype="")
            # Attachments
            with open(attachment['path'], 'rb') as file:
                email.attach(attachment['name'], file.read(), attachment['mime-type'])    # HTML content in the body
            # with open(f"{settings.MEDIA_ROOT}pdf/1/302/9d5d71f1-cf98-4825-ab6a-3133fa584450.pdf", 'rb') as file:
            #     email.attach("output1.pdf", file.read(), "application/pdf")
    
    if html_template:
        html_message = render_to_string(html_template, context)
        email.content_subtype = "html"
        email.body = html_message

    # Send the email
    email.send()

try:
    # Example usage:
    subject = 'Subject of the email'
    message = 'Plain text message'
    from_email = settings.BUSINESS_EMAIL
    recipient_list = ['parimal.patel@appaspect.com']
    bcc_list = ['parimal.patel@isaix.com']
    attachments = [
        {
            'path': f"{settings.MEDIA_ROOT}pdf/1/302/9d5d71f1-cf98-4825-ab6a-3133fa584450.pdf",
            'name': 'result.pdf',
            'mime-type': 'application/pdf'
        }
    ]
    html_template = '/home/techno200/projects/CyberApp/app/user/templates/admin-confirmation.html'
    context = {'variable': 'value'}  # Add any context data needed for rendering the HTML template

    send_custom_email(subject, message, from_email, recipient_list, bcc_list, attachments, html_template, context)

except Exception as e:
    print(e,"=>>>")
