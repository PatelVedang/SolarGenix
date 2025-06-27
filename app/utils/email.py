import logging
import threading
import traceback

# from auth_api.models import TokenType, User
from core.models import TokenType, User
from core.services.token_service import TokenService
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger("django")


def send_email(**kwargs):
    """
    Sends an email with optional HTML content, attachments, and dynamic context.

    Keyword Args:
        subject (str): Subject of the email.
        body (str): Plain text body of the email (HTML tags will be stripped).
        recipients (list): List of recipient email addresses.
        bcc (list, optional): List of BCC recipient email addresses.
        attachments (list, optional): List of attachments, each as a dict with keys:
            - "path": File path to the attachment.
            - "name": Name of the attachment file.
            - "mime-type": MIME type of the attachment.
        html_template (str, optional): Name of the HTML template (without .html extension) to render as the email body.
        html_string (str, optional): Raw HTML string to use as the email body (overrides html_template if provided).
        full_name (str, optional): Full name to be passed to the template context.
        otp (str, optional): OTP value to be passed to the template context.
        password (str, optional): Password to be passed to the template context.
        email (str, optional): Email address to be passed to the template context.
        button_links (list, optional): List of button links to be passed to the template context.

    Returns:
        bool: Always returns True, regardless of success or failure.

    Exceptions:
        Logs and prints any exceptions that occur during email sending.
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
                "otp": kwargs.get("otp", ""),
                "password": kwargs.get("password", ""),
                "email": kwargs.get("email", ""),
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
        self,
        subject,
        recipients,
        button_link,
        html_template,
        title,
        full_name,
        otp=None,
        password=None,
        email=None,
    ):
        """
        Creates a context dictionary for sending emails with customizable fields.

        Args:
            subject (str): The subject of the email.
            recipients (list): List of recipient email addresses.
            button_link (str or None): URL for the button in the email. If None, button_links is omitted from context.
            html_template (str): Path or identifier for the HTML template to use.
            title (str): Title to display in the email.
            full_name (str): Full name of the recipient.
            otp (str, optional): One-time password or code to include in the email. Defaults to None.
            password (str, optional): Password to include in the email. Defaults to None.
            email (str, optional): Email address to include in the context. Defaults to None.

        Returns:
            dict: A dictionary containing the email context to be used for rendering templates or sending emails.
        """
        context_dict = {
            "subject": subject,
            "user": self.user,
            "recipients": recipients,
            "button_links": [button_link],
            "html_template": html_template,
            "title": title,
            "full_name": full_name,  # Include full_name in context
            "otp": otp,
            "password": password,
            "email": email,
        }
        if otp:
            context_dict["otp"] = otp

        if password:
            context_dict["password"] = password

        if email:
            context_dict["email"] = email

        if button_link is None:
            context_dict.pop("button_links")
        return context_dict

    def send_verification_email(self):
        """
        Sends a verification email to the user with a unique verification token.

        This method generates a verification token for the user, constructs a verification link,
        prepares the email context with relevant details, and sends the verification email asynchronously.

        Returns:
            None
        """
        verify_token = TokenService.for_user(
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
        """
        Sends a password reset email to the specified email address.

        This method generates a password reset token for the current user, constructs a password reset link,
        and sends an email with the reset instructions to the provided email address.

        Args:
            email (str): The recipient's email address.

        Returns:
            None

        Side Effects:
            Sends an asynchronous email to the user with a password reset link.
        """
        reset_token = TokenService.for_user(
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
        """
        Sends a password update confirmation email to the user.
        This method constructs an email context with a confirmation message indicating that the user's password has been updated successfully.
        It includes a link to the login page and the user's full name in the email content, and sends the email asynchronously.
        Returns:
            None
        """

        button_link = f"{settings.FRONTEND_URL}/api/auth/login"
        full_name = f"{self.user.first_name} {self.user.last_name}"

        context = self.create_email_context(
            subject="Password Updated Successfully!",
            recipients=[self.user.email],
            html_template="reset_password_success",
            title="Password Updated Successfully",
            button_link=button_link,
            full_name=full_name,
        )
        self.send_email_async(context)

    def send_otp(self, otp):
        """
        Sends a One-Time Password (OTP) email to the user for password reset.

        Args:
            otp (str): The OTP code to be sent to the user.

        This method constructs the email context with the user's full name, a reset password link,
        and the OTP code, then sends the email asynchronously to the user's registered email address.
        """
        full_name = f"{self.user.first_name} {self.user.last_name}"
        button_link = f"{settings.FRONTEND_URL}/api/auth/reset-password-otp"
        context = self.create_email_context(
            subject="Your OTP code!",
            recipients=[self.user.email],
            html_template="send_otp",
            title="Reset your password",
            button_link=button_link,
            full_name=full_name,
            otp=otp,  # Pass the OTP to the email context
        )

        self.send_email_async(context)

    def send_email_superuser(self, password, email):
        """
        Sends a welcome email to a newly created superuser with their credentials.

        Args:
            password (str): The password assigned to the superuser.
            email (str): The email address of the superuser.

        Returns:
            bool: True if the email was sent successfully, False otherwise.

        Logs:
            Logs an error message if the email fails to send.
        """
        try:
            print(self.user.first_name)
            full_name = self.user.first_name
            button_link = f"{settings.FRONTEND_URL}/admin/"
            email = self.user.email
            context = self.create_email_context(
                subject="Admin created successfully!",
                recipients=[self.user.email],
                html_template="superuser",
                title="Welcome on board!",
                button_link=button_link,
                full_name=full_name,
                password=password,  # Pass the password to the email context
                email=email,
            )

            self.send_email_async(context)
            return True
        except Exception as e:
            logger.error(f"Failed to send email for superuser creation: {e}")
            return False

    def send_verification_email_by_admin(self, password, email):
        """
        Sends a verification email to a user, typically triggered by an admin action.

        This method generates a verification token for the user, constructs an email context
        with the provided password and email, and sends a verification email asynchronously.
        If the email fails to send, the error is logged and the method returns False.

        Args:
            password (str): The password to include in the email context.
            email (str): The recipient's email address.

        Returns:
            bool: True if the email was sent successfully, False otherwise.
        """
        try:
            verify_token = TokenService.for_user(
                self.user,
                TokenType.VERIFY_MAIL.value,
                settings.AUTH_VERIFY_EMAIL_TOKEN_LIFELINE,
            )
            full_name = f"{self.user.first_name} {self.user.last_name}"
            button_link = (
                f"{settings.FRONTEND_URL}/api/auth/verify-email/{verify_token}"
            )
            context = self.create_email_context(
                subject=f"Welcome to Our Community, {full_name}",
                recipients=[self.user.email],
                button_link=button_link,
                html_template="create_user",
                title="Verify Your E-mail Address",
                full_name=full_name,
                password=password,
                email=email,
            )
            self.send_email_async(context)
            return True
        except Exception as e:
            logger.error(f"Failed to send email {e}")
            return False
