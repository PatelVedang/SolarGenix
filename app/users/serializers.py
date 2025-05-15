import random
import string
import threading

from auth_api.models import SimpleToken, TokenType, User
from django.conf import settings
from proj.base_serializer import BaseModelSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from utils.custom_exception import CustomValidationError
from utils.email import send_email
from users.constants import UserResponseConstants

class UserSerializer(BaseModelSerializer):
    email = serializers.EmailField(
        error_messages={
            "unique": "A user with this email already exists!",
            "invalid": "Please enter a valid email address.",
        }
    )

    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "is_active"]
        read_only_fields = ["id", "is_active"]

    def validate(self, attrs):
        email = attrs.get("email").strip().lower()

        if User.objects.filter(email=email).exists():
            raise CustomValidationError(UserResponseConstants.EMAIL_ALREADY_EXISTS)
        return attrs

    @staticmethod
    def generate_password():
        """Generates a random password."""
        try:
            return "".join(
                random.choices(
                    f"{string.ascii_letters}{string.digits}{string.punctuation}".replace(
                        '"', ""
                    ).replace("'", ""),
                    k=10,
                )
            )
        # allowed_characters =
        except Exception as e:
            print(f"Error generating password: {e}")
            return None

    def create(self, validated_data):
        # Always generate a new password
        raw_password = self.generate_password()
        if not raw_password:
            raise CustomValidationError(UserResponseConstants.ERROR_GENERATING_PASS)

        validated_data["password"] = raw_password
        validated_data["is_active"] = False  # Activate the user

        try:
            user = User.objects.create_user(**validated_data)
            # Send email with the generated password
            try:
                verify_token = SimpleToken.for_user(
                    user,
                    TokenType.VERIFY_MAIL.value,
                    settings.AUTH_VERIFY_EMAIL_TOKEN_LIFELINE,
                )
                context = {
                    "subject": f"Welcome to Our Community, {user.first_name}!",
                    "user": user,
                    "password": raw_password,
                    "recipients": [user.email],
                    "button_links": [
                        f"{settings.FRONTEND_URL}/api/auth/verify-email/{verify_token}"
                    ],
                    "html_template": "user_created_by_admin",
                    "title": "Verify Your E-mail Address",
                }
                thread = threading.Thread(target=send_email, kwargs=context)
                thread.start()

            except Exception as e:
                print(f"Error sending email: {e}")
                raise CustomValidationError(UserResponseConstants.ERROR_SENDING_EMAIL)

            return user
        except Exception as e:
            raise CustomValidationError(str(e))

    def update(self, instance, validated_data):
        email = validated_data.get("email", None)
        if email and User.objects.exclude(pk=instance.pk).filter(email=email).exists():
            raise ValidationError({"email": UserResponseConstants.EMAIL_ALREADY_EXISTS})

        return super().update(instance, validated_data)


class UserExportSerializer(BaseModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "is_email_verified",
            "is_default_password",
            "is_active",
            "is_staff",
            "is_superuser",
            "is_deleted",
            "created_at",
            "updated_at",
            "date_joined",
            "last_login",
        ]
        read_only_fields = ["id", "is_active"]