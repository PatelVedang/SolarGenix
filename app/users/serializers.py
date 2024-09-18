from proj.base_serializer import DynamicFieldsSerializer
from auth_api.models import User

from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.auth.hashers import make_password

from rest_framework.exceptions import ValidationError
from rest_framework.serializers import CharField

import random
import string


class UserSerializer(DynamicFieldsSerializer):
    password = CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = "__all__"

    @staticmethod
    def generate_password(self):
        # Generate a random password meeting the criteria
        try:
            password = "".join(
                random.choices(
                    string.ascii_letters + string.digits + string.punctuation, k=10
                )
            )
            return password
        except Exception as e:
            print(f"Error generating password: {e}")
            return None

    def create(self, validated_data):
        email = validated_data.get("email", None)
        first_name = validated_data.get("first_name", "")
        last_name = validated_data.get("last_name", "")

        if "password" not in validated_data or validated_data["password"] == "":
            raw_password = UserSerializer.generate_password(self)
            if raw_password is None:
                raise ValidationError("Error generating password.")
            validated_data["password"] = make_password(raw_password)
            validated_data["is_active"] = True
            # Send email with the generated password
            try:
                UserSerializer.send_email(
                    self, email, raw_password, first_name, last_name
                )
            except Exception as e:
                print(f"Error sending email: {e}")
                raise ValidationError("Error sending email.")
        else:
            validated_data["password"] = make_password(validated_data["password"])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        email = validated_data.get("email", None)
        if email and User.objects.exclude(pk=instance.pk).filter(email=email).exists():
            raise ValidationError({"email": "This email is already in use."})

        return super().update(instance, validated_data)

    def send_email(self, email, password, first_name, last_name):
        subject = "Your Auto-Generated Password"
        html_message = render_to_string(
            "user-with-credentials.html",
            {
                "email": email,
                "user_name": first_name + " " + last_name,
                "password": password,
            },
        )
        email_message = EmailMessage(
            subject, html_message, from_email=settings.EMAIL_HOST_USER, to=[email]
        )
        email_message.content_subtype = "html"
        email_message.send()
