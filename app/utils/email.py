from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import traceback
from utils.constant import EmailTemplates
import logging

logger = logging.getLogger("django")


def send_email(**kwargs):
    subject = kwargs.get("subject", "")
    body = kwargs.get("body", "")
    sender = kwargs.get("sender")
    recipients = kwargs.get("recipients", [])
    bcc = kwargs.get("bcc", [])
    attachments = kwargs.get("attachments", [])
    html_template = kwargs.get("html_template", "")
    html_string = kwargs.get("html_string", "")
    # button_links = kwargs.get("button_links", [])
    title = kwargs.get("title", "")

    logger.info("***************** SEND MAIL  *****************")
    logger.info(f"Recipients: {recipients}")
    try:
        email = EmailMessage(subject, strip_tags(body), sender, recipients, bcc=bcc)
        print("email", email)
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
        print(f"response {email}")
        print("Please check your inbox.")
    except Exception as e:
        print(e, "=>>>>>>>>>>>>Error")
        traceback.print_exc()
        logger.error(str(e))

    return True
