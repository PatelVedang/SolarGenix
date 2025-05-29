import logging
import threading
import traceback

from auth_api.models import SimpleToken, TokenType, User
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger("django")


def send_email(**kwargs):
    """
    Sends an email with optional subject, body, recipients, attachments,
    and HTML content using a template or string.
    """
    try:
        # Create the email message
        email = EmailMessage(
            kwargs.get("subject", ""),
            strip_tags(kwargs.get("body", "")),  # Strip tags for the text version
            f"{settings.EMAIL_FORM_NAME} <{settings.EMAIL_HOST_USER}>",
            kwargs.get("recipients", []),
            bcc=kwargs.get("bcc", []),
        )

        # Handle attachments if provided
        for attachment in kwargs.get("attachments", []):
            with open(attachment["path"], "rb") as file:
                email.attach(attachment["name"], file.read(), attachment["mime-type"])

        # Render the HTML content directly using the forgot_password template
        if html_template := kwargs.get("html_template", ""):
            button_link = kwargs.get("button_links", "#")
            # Pass the dynamic data (full_name, button_link, etc.) to the template
            context = {
                "full_name": kwargs.get("full_name", ""),
                "button_link": button_link[0],
            }
            # Render the HTML template with the provided context
            html_message = render_to_string(f"{html_template}.html", context)

            # Set the email body and content type to HTML
            email.body, email.content_subtype = html_message, "html"

        elif html_string := kwargs.get("html_string", ""):
            email.body, email.content_subtype = html_string, "html"

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
        self, subject, recipients, button_link, html_template, title, full_name
    ):
        """Creates a context dictionary for email sending."""

        context_dict = {
            "subject": subject,
            "user": self.user,
            "recipients": recipients,
            "button_links": [button_link],
            "html_template": html_template,
            "title": title,
            "full_name": full_name,  # Include full_name in context
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
        full_name = f"{self.user.first_name} {self.user.last_name}"
        button_link = f"{settings.FRONTEND_URL}/api/auth/verify-email/{verify_token}"
        context = self.create_email_context(
            subject="Verify Your E-mail Address!",
            recipients=[self.user.email],
            button_link=button_link,
            html_template="email_verification",
            title="Verify Your E-mail Address",
            full_name=full_name,
        )
        self.send_email_async(context)

    def send_password_reset_email(self, email: str):
        reset_token = SimpleToken.for_user(
            self.user,
            TokenType.RESET.value,
            settings.AUTH_RESET_PASSWORD_TOKEN_LIFELINE,
        )
        full_name = f"{self.user.first_name} {self.user.last_name}"
        button_link = f"{settings.FRONTEND_URL}/api/auth/reset-password/{reset_token}"

        context = self.create_email_context(
            subject="Password Reset Request",
            recipients=[email],
            button_link=button_link,
            html_template="forgot_password",
            title="Reset your password",
            full_name=full_name,
        )
        self.send_email_async(context)

    def send_password_update_confirmation(self):
        full_name = f"{self.user.first_name} {self.user.last_name}"
        button_link = f"{settings.FRONTEND_URL}/api/auth/login"

        context = self.create_email_context(
            subject="Password Updated Successfully!",
            recipients=[self.user.email],
            html_template="reset_password_success",
            title="Password Updated Successfully",
            button_link=button_link,
            full_name=full_name,
        )
        self.send_email_async(context)

    # def send_otp(self):
    #     reset_token = SimpleToken.for_user(
    #         user,
    #         TokenType.OTP.value,
    #         settings.OTP_EXPIRY_MINUTES,
    #         str(otp),
    #     )
