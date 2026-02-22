import random
import string
import threading

# from auth_api.models import  TokenType, User
from core.models import TokenType, User
from core.services.token_service import TokenService
from django.conf import settings
from proj.base_serializer import BaseModelSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from users.constants import UserResponseConstants
from utils.custom_exception import CustomValidationError


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
        except Exception as e:
            raise CustomValidationError(str(e))

        return user

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
