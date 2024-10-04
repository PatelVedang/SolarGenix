import logging
import traceback

from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from utils.constant import EmailTemplates

logger = logging.getLogger("django")


def send_email(**kwargs):
    """
    Sends an email with optional subject, body, recipients, attachments,
    and HTML content using a template or string.
    """

    try:
        email = EmailMessage(
            kwargs.get("subject", ""),
            strip_tags(kwargs.get("body", "")),
            f"{settings.EMAIL_FORM_NAME} <{settings.EMAIL_HOST_USER}>",
            kwargs.get("recipients", []),
            bcc=kwargs.get("bcc", []),
        )

        for attachment in kwargs.get("attachments", []):
            with open(attachment["path"], "rb") as file:
                email.attach(attachment["name"], file.read(), attachment["mime-type"])

        if html_template := kwargs.get("html_template", ""):
            content = EmailTemplates(html_template, **kwargs).result
            html_message = render_to_string(
                "email-template.html",
                {"content": content, "title": kwargs.get("title", "")},
            )
            email.body, email.content_subtype = html_message, "html"

        elif html_string := kwargs.get("html_string", ""):
            email.body, email.content_subtype = html_string, "html"

        email.send()
        print("Mail sent please check your inbox")

    except Exception as e:
        traceback.print_exc()
        logger.error(str(e))

    return True
