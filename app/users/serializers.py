import random
import string


from django.conf import settings
from proj.base_serializer import BaseModelSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

# from auth_api.models import SimpleToken, TokenType, User
from user_auth.models import SimpleToken, TokenType, User
from utils.custom_exception import CustomValidationError
from utils.email import EmailService


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
            raise CustomValidationError("A user with this email already exists!")
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
            raise CustomValidationError("Error generating password")

        validated_data["password"] = raw_password
        validated_data["is_active"] = True  # Activate the user


        try:
            user = User.objects.create_user(**validated_data)
            user.save()
            email_service = EmailService(user)
            email_sent = email_service.send_verification_email_by_admin(
                password=raw_password, email=user.email
            )
            if not email_sent:
                self.stdout.write(
                    self.style.ERROR(
                        "Failed to send email for user creation. Rolling back."
                    )
                )
                return

            return user
        except Exception as e:
            raise CustomValidationError(str(e))

    def update(self, instance, validated_data):
        email = validated_data.get("email", None)
        if email and User.objects.exclude(pk=instance.pk).filter(email=email).exists():
            raise ValidationError({"email": "This email is already in use."})

        return super().update(instance, validated_data)
