import random
import string

from auth_api.models import User
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from proj.base_serializer import BaseModelSerializer
from rest_framework.exceptions import ValidationError
from utils.custom_exception import CustomValidationError


class UserSerializer(BaseModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "is_active",
            "date_joined",
            "last_login",
        ]
        read_only_fields = ["id", "is_active"]

    @staticmethod
    def generate_password():
        """Generates a random password."""
        try:
            return "".join(
                random.choices(
                    string.ascii_letters + string.digits + string.punctuation, k=10
                )
            )
        except Exception as e:
            print(f"Error generating password: {e}")
            return None

    def create(self, validated_data):
        email = validated_data.get("email", None)
        first_name = validated_data.get("first_name", "")
        last_name = validated_data.get("last_name", "")

        # Always generate a new password
        raw_password = self.generate_password()
        raw_password = None
        if not raw_password:
            raise CustomValidationError("Error generating password")

        validated_data["password"] = raw_password
        validated_data["is_active"] = True  # Activate the user

        try:
            user = User.objects.create_user(**validated_data)
            # Send email with the generated password
            try:
                self.send_email(email, raw_password, first_name, last_name)
            except Exception as e:
                print(f"Error sending email: {e}")
                raise ValidationError("Error sending email.")
            return user
        except Exception as e:
            raise ValidationError(str(e))

    def update(self, instance, validated_data):
        email = validated_data.get("email", None)
        if email and User.objects.exclude(pk=instance.pk).filter(email=email).exists():
            raise ValidationError({"email": "This email is already in use."})

        return super().update(instance, validated_data)

    @staticmethod
    def send_email(email, password, first_name, last_name):
        """Sends an email with the auto-generated password."""
        subject = "Your Auto-Generated Password"
        html_message = render_to_string(
            "user-with-credentials.html",
            {
                "email": email,
                "user_name": f"{first_name} {last_name}",
                "password": password,
            },
        )
        email_message = EmailMessage(
            subject, html_message, from_email=settings.EMAIL_HOST_USER, to=[email]
        )
        email_message.content_subtype = "html"
        email_message.send()
