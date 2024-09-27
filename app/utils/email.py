import logging
import traceback

from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from utils.constant import EmailTemplates

logger = logging.getLogger("django")


def send_email(**kwargs):
    """This function sends an email to the recipients with the given subject and body.
    kwargs = {
        "subject": "Subject of the email",
        "body": "Body of the email",
        "sender": "Sender of the email",
        "recipients": ["
            List of recipients
        "],
        "bcc": [
            List of BCC recipients
        ],
        "attachments": [
            {
                "path": "Path to the attachment",
                "name": "Name of the attachment",
                "mime-type": "MIME type of the attachment"
            }
        ],
        "html_template": "Name of the HTML template",
        "html_string": "HTML content in the body",
        "title": "Title of the email"
    }
    All fields are optional except for the recipients. If the HTML template is provided, the email will be sent with the HTML content in the body.
    """

    subject = kwargs.get("subject", "")
    body = kwargs.get("body", "")
    sender = kwargs.get("sender")
    recipients = kwargs.get("recipients", [])
    bcc = kwargs.get("bcc", [])
    attachments = kwargs.get("attachments", [])
    html_template = kwargs.get("html_template", "")
    html_string = kwargs.get("html_string", "")
    title = kwargs.get("title", "")

    logger.info("***************** SEND MAIL  *****************")
    logger.info(f"Recipients: {recipients}")
    try:
        email = EmailMessage(
            subject,
            strip_tags(body),
            f"{settings.FORM_TITLE}  <{sender}>",
            recipients,
            bcc=bcc,
        )
        # Attachments
        if attachments:
            for attachment in attachments:
                with open(attachment["path"], "rb") as file:
                    email.attach(
                        attachment["name"], file.read(), attachment["mime-type"]
                    )  # HTML content in the body

        # # HTML content in the body
        if html_template:
            template = EmailTemplates(html_template, **kwargs)
            content = template.result

            # Prepare the final email content
            context = {"content": content, "title": title}
            html_message = render_to_string("email-template.html", context)
            email.content_subtype = "html"
            email.body = html_message

        if html_string:
            html_message = html_string
            email.content_subtype = "html"
            email.body = html_message
        # Send the email
        email.send()
        print("Mail sent please check your inbox")
    except Exception as e:
        traceback.print_exc()
        logger.error(str(e))

    return True
