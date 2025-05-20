from django.template import Context, Template


class EmailTemplates:
    """
    A class for generating email templates with dynamic content.

    This class provides various email templates for different purposes such as
    forgot password, reset password, email verification, and resending reset password email.
    The templates are rendered with the provided context data.

    Attributes:
        html_str (str): HTML string template for the email content.
        templates (dict): Dictionary mapping template names to their corresponding methods.
        result (str): Rendered HTML content of the selected email template.

    Methods:
        forgot_password(**kwargs): Generates the forgot password email content.
        reset_password(**kwargs): Generates the reset password email content.
        verify_email(**kwargs): Generates the email verification content.
        resend_reset_password(**kwargs): Generates the resend reset password email content.
    """

    def __init__(self, template_name, **kwargs) -> None:
        """
        Initializes the EmailTemplates class with the specified template name and context data.

        Args:
            template_name (str): The name of the template to be used.
            **kwargs: Additional context data to be used in the template.

        Returns:
            None
        """

        self.html_str = """
        <table
        style="font-family: 'Poppins', sans-serif"
        role="presentation"
        cellpadding="0"
        cellspacing="0"
        width="100%"
        border="0"
        >
        <tbody>
            <tr>
            <td
                style="
                overflow-wrap: break-word;
                word-break: break-word;
                padding: 33px 55px 30px 55px;
                font-family: 'Poppins', sans-serif;
                "
                align="left"
            >
                <div
                style="
                    font-size: 14px;
                    line-height: 160%;
                    text-align: center;
                    word-wrap: break-word;
                "
                >
                {%for line in lines%}
                <p style="font-size: 14px; line-height: 160%">
                    <span style="font-size: 22px; line-height: 35.2px"
                    >{{line}}
                    </span>
                </p>
                {% endfor %}
                </div>
            </td>
            </tr>
        </tbody>
        </table>
        {% if button_label %}
        <table
        style="font-family: 'Poppins', sans-serif"
        role="presentation"
        cellpadding="0"
        cellspacing="0"
        width="100%"
        border="0"
        >
        <tbody>
            <tr>
            <td
                style="
                overflow-wrap: break-word;
                word-break: break-word;
                padding: 10px;
                font-family: 'Poppins', sans-serif;
                "
                align="left"
            >
                <div align="center">
                <a
                    href="{{button_link}}"
                    target="_blank"
                    class="v-button"
                    style="
                    box-sizing: border-box;
                    display: inline-block;
                    font-family: 'Poppins', sans-serif;
                    text-decoration: none;
                    -webkit-text-size-adjust: none;
                    text-align: center;
                    color: #ffffff;
                    background-color: #ff6600;
                    border-radius: 4px;
                    -webkit-border-radius: 4px;
                    -moz-border-radius: 4px;
                    width: auto;
                    max-width: 100%;
                    overflow-wrap: break-word;
                    word-break: break-word;
                    word-wrap: break-word;
                    mso-border-alt: none;
                    font-size: 14px;
                    "
                >
                    <span
                    style="display: block; padding: 14px 44px 13px; line-height: 120%"
                    ><span style="font-size: 16px; line-height: 19.2px"
                        ><strong
                        ><span
                            style="
                            line-height: 19.2px;
                            font-size: 16px;
                            text-transform: uppercase;
                            "
                            >{{button_label}}</span
                        ></strong
                        >
                    </span>
                    </span>
                </a>
                </div>
            </td>
            </tr>
            {% if verify_details %}
            <tr>
                <td
                    style="
                    overflow-wrap: break-word;
                    word-break: break-word;
                    padding: 33px 55px 30px 55px;
                    font-family: 'Poppins', sans-serif;
                    "
                    align="left"
                >
                    <div
                    style="
                        font-size: 14px;
                        line-height: 160%;
                        text-align: center;
                        word-wrap: break-word;
                    "
                    >
                    {%for line in verify_details%}
                    <p style="font-size: 14px; line-height: 160%">
                        <span style="font-size: 22px; line-height: 35.2px"
                        >{{line}}
                        </span>
                    </p>
                    {% endfor %}
                    </div>
                </td>
                </tr>
            {% endif%}
        </tbody>
        </table>
        {% endif %}
        """
        self.templates = {
            "forgot_password": self.forgot_password,
            "reset_password": self.reset_password,
            "verify_email": self.verify_email,
            "resend_reset_password": self.resend_reset_password,
            "superuser_created": self.superuser_created,
            "user_created_by_admin": self.user_created_by_admin,
            "otp_email_template": self.otp_email_template,
        }
        self.result = self.templates[template_name](**kwargs)

    def forgot_password(self, **kwargs):
        """
        The `forgot_password` function generates an HTML email template for resetting a user's password.
        :return: The `forgot_password` method returns an HTML content for a password reset email template.
        """
        user = kwargs.get("user")
        button_label = "Reset Password"
        button_link = kwargs.get("button_links", "#")

        lines = [
            f"Hello {user.first_name} {user.last_name},",
            "We received a request to reset your password. If you did not make this request, please ignore this email.",
            "To reset your password, please click on the link below:",
        ]

        context = {
            "lines": lines,
            "button_label": button_label,
            "button_link": button_link[0],
        }
        template = Template(self.html_str)
        html_content = template.render(Context(context))
        return html_content

    def reset_password(self, **kwargs):
        """
        The `reset_password` function generates an HTML email template for notifying a user about a
        successful password reset.
        :return: The `reset_password` method returns the HTML content for an email template with a message
        confirming the successful reset of a user's password. The content includes a greeting with the
        user's first and last name, instructions to use the new password for login, and a reminder to
        contact support if the password reset was not initiated by the user.
        """
        user = kwargs.get("user")
        button_label = "Login"
        button_link = kwargs.get("button_links", "#")

        lines = [
            f"Hello {user.first_name} {user.last_name},",
            "Your password has been successfully reset. Please use your new password to login.",
            "If you did not initiate this password reset, please contact our support team immediately.",
        ]
        context = {
            "lines": lines,
            "button_label": button_label,
            "button_link": button_link[0],
        }
        template = Template(self.html_str)
        html_content = template.render(Context(context))
        return html_content

    def verify_email(self, **kwargs):
        """
        The `verify_email` function generates an HTML email template with a verification button for a user's
        email address.
        :return: The `verify_email` method returns the HTML content generated based on the provided user
        information and button link.
        """
        user = kwargs.get("user")
        button_label = "VERIFY YOUR EMAIL"
        button_link = kwargs.get("button_links", "#")

        lines = [
            f"Hello {user.first_name} {user.last_name},",
            "You're almost ready to get started. Please click on the button below to verify your email address.",
        ]
        context = {
            "lines": lines,
            "button_label": button_label,
            "button_link": button_link[0],
        }
        template = Template(self.html_str)
        html_content = template.render(Context(context))
        return html_content

    def resend_reset_password(self, **kwargs):
        """
        The function `resend_reset_password` generates an HTML email template to notify the user
        that their password has been successfully updated.
        :return: the HTML content for a password update confirmation email, with personalized information such as
        the user's first and last name, a message about the successful password update, and a link for future account management.
        """
        user = kwargs.get("user")
        button_label = "Login"
        button_link = kwargs.get("button_links", "#")

        lines = [
            f"Hello {user.first_name} {user.last_name},",
            "Your password has been successfully updated. If you did not make this change, please contact us immediately.",
            "You can manage your account settings by login again, please click on the link below:",
        ]

        context = {
            "lines": lines,
            "button_label": button_label,
            "button_link": button_link[0],
        }
        template = Template(self.html_str)
        html_content = template.render(Context(context))
        return html_content

    def superuser_created(self, **kwargs):
        """
        The function `superuser_created` generates an HTML email content welcoming a new superuser to the
        community and providing login credentials.
        :return: The `superuser_created` method returns an HTML content for an email template that includes
        a welcome message for a new user who has joined the community. The email includes the user's first
        name, login credentials (email and password), and a button link for logging in.
        """
        user = kwargs.get("user")
        password = kwargs.get("password")
        button_link = kwargs.get("button_links", "#")

        lines = [
            f"Dear {user.first_name},",
            "Thank you for joining our community. We're thrilled to have you on board.",
            "Please use the below credentials to log in to the app:",
            f"Email: {user.email}",
            f"Password: {password}",
        ]

        context = {
            "lines": lines,
            "button_label": "Login",  # No button for this email
            "button_link": button_link[0],
        }
        template = Template(self.html_str)
        html_content = template.render(Context(context))
        return html_content

    def user_created_by_admin(self, **kwargs):
        """
        The function generates an HTML email content to notify a user that their account has been
        created by an admin, providing login details and instructions for email verification.
        :return: the HTML content for an email template that is created when a user is successfully
        created by an admin. The email includes a welcome message, login details (email and password), a
        verification link for the user's email address, instructions for account activation, and a
        message welcoming the user to the community.
        """
        user = kwargs.get("user")
        password = kwargs.get("password")
        lines = [
            f"Dear {user.first_name} {user.last_name},",
            "We’re excited to welcome you to our community!",
            "Your account has been successfully created by an admin. Here are your login details:",  # noqa: E501
            f"Email : {user.email}",
            f"Password : {password}",
            "To activate your account, please verify your email address by clicking the button below:",  # noqa: E501
        ]
        verify_details = [
            "Once your email is verified, you can log in using the credentials provided above.",  # noqa: E501
            "If you have any questions or need assistance, feel free to reach out to our support team.",  # noqa: E501
            "Welcome aboard! We hope you enjoy your experience with us!",
        ]
        user = kwargs.get("user")
        button_label = "VERIFY YOUR EMAIL"
        button_link = kwargs.get("button_links", "#")

        context = {
            "lines": lines,
            "button_label": button_label,  # No button for this email
            "button_link": button_link[0],
            "verify_details": verify_details,
        }
        template = Template(self.html_str)
        html_content = template.render(Context(context))
        return html_content

    def otp_email_template(self, **kwargs):
        """
        The `otp_email_template` function generates an HTML email template for sending a one-time password (OTP) to the user
        for verifying their identity during the password reset process.
        """
        user = kwargs.get("user")
        otp = kwargs.get("otp")
        button_label = "Verify OTP"
        button_link = kwargs.get("button_links", "#")

        lines = [
            f"Hello {user.first_name} {user.last_name},",
            f"To reset your password, use the following OTP: {otp}.",
            "To verify the OTP and continue with resetting your password, please click on the link below:",
            "If you did not make this request, please ignore this email.",
        ]

        context = {
            "lines": lines,
            "button_label": button_label,
            "button_link": button_link[0],
        }
        template = Template(self.html_str)
        html_content = template.render(Context(context))
        return html_content
