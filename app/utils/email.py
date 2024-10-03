import logging
import threading
import traceback

from auth_api.models import SimpleToken, TokenType, User
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
            f"{settings.EMAIL_FORM_NAME}  <{settings.EMAIL_HOST_USER}>",
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


class EmailService:
    def __init__(self, user: User):
        self.user = user

    def send_email_async(self, context):
        """Helper function to send email in a separate thread."""
        thread = threading.Thread(target=send_email, kwargs=context)
        thread.start()

    def create_email_context(
        self, subject, recipients, button_link, html_template, title
    ):
        """Creates a context dictionary for email sending."""

        print("context====", button_link, recipients)
        context_dict = {
            "subject": subject,
            "user": self.user,
            "recipients": recipients,
            "button_links": [button_link],
            "html_template": html_template,
            "title": title,
        }
        if button_link is None:
            context_dict.pop("button_links")
        return context_dict

    def send_verification_email(self):
        verify_token = SimpleToken.for_user(
            self.user,
            TokenType.VERIFY_MAIL.value,
            settings.AUTH_VERIFY_EMAIL_TOKEN_LIFELINE,
        )
        button_link = f"{settings.FRONTEND_URL}/api/auth/verify-email/{verify_token}"
        context = self.create_email_context(
            subject="Verify Your E-mail Address!",
            recipients=[self.user.email],
            button_link=button_link,
            html_template="verify_email",
            title="Verify Your E-mail Address",
        )
        self.send_email_async(context)

    def send_password_reset_email(self, email: str):
        reset_token = SimpleToken.for_user(
            self.user,
            TokenType.RESET.value,
            settings.AUTH_RESET_PASSWORD_TOKEN_LIFELINE,
        )
        button_link = f"{settings.FRONTEND_URL}/api/auth/reset-password/{reset_token}"
        context = self.create_email_context(
            subject="Password Reset Request",
            recipients=[email],
            button_link=button_link,
            html_template="forgot_password",
            title="Reset your password",
        )
        self.send_email_async(context)

    def send_password_update_confirmation(self):
        context = self.create_email_context(
            subject="Password Updated Successfully!",
            recipients=[self.user.email],
            html_template="resend_reset_password",
            title="Password Updated Successfully",
            button_link=None,
        )
        self.send_email_async(context)
