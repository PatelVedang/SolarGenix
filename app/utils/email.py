import logging
import threading
import traceback

from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags

# from auth_api.models import SimpleToken, TokenType, User
from user_auth.models import SimpleToken, TokenType, User
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
