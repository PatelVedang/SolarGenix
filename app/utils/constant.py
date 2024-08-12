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
        </tbody>
        </table>
        {% endif %}
        """
        self.templates = {
            "forgot_password": self.forgot_password,
            "reset_password": self.reset_password,
            "verify_email": self.verify_email,
            "resend_reset_password": self.resend_reset_password,
        }
        self.result = self.templates[template_name](**kwargs)

    def forgot_password(self, **kwargs):
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
        user = kwargs.get("user")

        lines = [
            f"Hello {user.first_name} {user.last_name},",
            "Your password has been successfully reset. Please use your new password to login.",
            "If you did not initiate this password reset, please contact our support team immediately.",
        ]
        context = {
            "lines": lines,
        }
        template = Template(self.html_str)
        html_content = template.render(Context(context))
        return html_content

    def verify_email(self, **kwargs):
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
