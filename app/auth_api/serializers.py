import logging
import re
import threading

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from proj.base_serializer import BaseSerializer
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from utils.email import send_email

from auth_api.models import SimpleToken, Token, TokenType, User

from .google import Google

logger = logging.getLogger("django")


# The `UserRegistrationSerializer` class handles user registration data validation and creation,
# including checking for existing email, password validation, and sending a verification email.
class UserRegistrationSerializer(BaseSerializer):
    password = serializers.CharField(style={"input_type": "password"}, write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "password", "confirm_password"]

    def validate(self, attrs):
        password = attrs.get("password")
        confirm_pasword = attrs.pop("confirm_password")

        if User.objects.filter(email=attrs.get("email").lower()).exists():
            raise serializers.ValidationError("Email already exists.")

        if not re.search(settings.PASSWORD_VALIDATE_REGEX, password):
            raise serializers.ValidationError(settings.PASSWORD_VALIDATE_STRING)

        if password != confirm_pasword:
            raise serializers.ValidationError("Passwords do not match.")

        return attrs

    def create(self, validated_data):
        validated_data["email"] = validated_data["email"].lower()
        user = super().create(validated_data)
        user.set_password(validated_data["password"])
        user.save()
        verify_token = SimpleToken.for_user(
            user, TokenType.VERIFY_MAIL.value, settings.AUTH_VERIFY_EMAIL_TOKEN_LIFELINE
        )
        context = {
            "subject": "Verify Your E-mail Address!",
            "user": user,
            "recipients": [user.email],
            "button_links": [
                f"{settings.HOST_URL}/api/auth/verify-email/{verify_token}"
            ],
            "html_template": "verify_email",
            "title": "Verify Your E-mail Address",
        }
        thread = threading.Thread(target=send_email, kwargs=context)
        thread.start()
        return user


class UserLoginSerializer(BaseSerializer):
    email = serializers.EmailField(max_length=255)

    class Meta:
        model = User
        fields = ["email", "password"]

    def validate(self, attrs):
        attrs["email"] = attrs["email"].lower()
        # Authenticate the user with provided credentials
        user = authenticate(**attrs)
        if not user:
            user = User.objects.filter(email=attrs.get("email"), is_active=False)
            if user.exists():
                user = user.first()
                verify_token = SimpleToken.for_user(
                    user,
                    TokenType.VERIFY_MAIL.value,
                    settings.AUTH_VERIFY_EMAIL_TOKEN_LIFELINE,
                )
                context = {
                    "subject": "Verify Your E-mail Address!",
                    "user": user,
                    "recipients": [user.email],
                    "button_links": [
                        f"{settings.HOST_URL}/api/auth/verify-email/{verify_token}"
                    ],
                    "html_template": "verify_email",
                    "title": "Verify Your E-mail Address",
                }
                thread = threading.Thread(target=send_email, kwargs=context)
                thread.start()
                raise serializers.ValidationError(
                    "Email not verified. Please check your email for verification link."
                )
            raise serializers.ValidationError("Invalid email or password")

        if not user.is_active:
            raise serializers.ValidationError(
                "Email not verified. Please check your email."
            )
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "email"]


class ForgotPasswordSerializer(BaseSerializer):
    email = serializers.EmailField(
        max_length=255, required=True, allow_blank=False, allow_null=False
    )

    class Meta:
        model = User
        fields = ["email"]

    def validate(self, attrs):
        email = attrs.get("email").lower()
        user = User.objects.filter(email=email)
        if user.exists():
            user = user.first()
            Token.objects.filter(user=user, token_type="reset").delete()
            reset_token = SimpleToken.for_user(
                user, TokenType.RESET.value, settings.AUTH_RESET_PASSWORD_TOKEN_LIFELINE
            )
            context = {
                "subject": "Password Reset Request",
                "user": user,
                "recipients": [email],
                "html_template": "forgot_password",
                "button_links": [
                    f"{settings.HOST_URL}/api/auth/reset-password/{reset_token}"
                ],
                "title": "Reset your password",
            }
            thread = threading.Thread(target=send_email, kwargs=context)
            thread.start()
        else:
            logger.error(f"Forgot password mail sent fail due to {email} not found")
        return attrs


class ResendResetTokenSerializer(BaseSerializer):
    email = serializers.EmailField(
        max_length=255, label="Test", error_messages={"invalid": "ddd"}
    )

    class Meta:
        model = User
        fields = ["email"]

    def validate(self, attrs):
        email = attrs.get("email").lower()
        user = User.objects.filter(email=email)
        if user.exists():
            user = user.first()
            Token.objects.filter(user=user, token_type="reset").delete()
            token = SimpleToken.for_user(
                user, TokenType.RESET.value, settings.AUTH_RESET_PASSWORD_TOKEN_LIFELINE
            )
            context = {
                "subject": "Resend Password Reset Request",
                "user": user,
                "recipients": [email],
                "html_template": "resend_reset_password",
                "button_links": [
                    f"{settings.HOST_URL}/api/auth/reset-password/{token}"
                ],
                "title": "Reset your password",
            }
            thread = threading.Thread(target=send_email, kwargs=context)
            thread.start()
        else:
            logger.error(
                f"Resend forgot password mail sent fail due to {email} not found"
            )  # noqa: E501
        return attrs


class UserPasswordResetSerializer(BaseSerializer):
    password = serializers.CharField(style={"input_type": "password"}, write_only=True)
    confirm_password = serializers.CharField(
        style={"input_type": "password"}, write_only=True
    )

    class Meta:
        model = User
        fields = ["password", "confirm_password"]

    def validate(self, attrs):
        password = attrs.get("password")
        confirm_pasword = attrs.get("confirm_password")
        token = self.context.get("token")

        if not re.search(settings.PASSWORD_VALIDATE_REGEX, attrs.get("password")):
            raise serializers.ValidationError(settings.PASSWORD_VALIDATE_STRING)

        if password != confirm_pasword:
            raise serializers.ValidationError("Passwords do not match.")

        payload = SimpleToken.validate_token(token, TokenType.RESET.value)
        token_obj = payload.get("token_obj")
        user = token_obj.user
        user.password = make_password(password)
        user.save()
        token_obj.hard_delete()
        context = {
            "subject": "Password updated successfully!",
            "user": user,
            "recipients": [user.email],
            "html_template": "resend_reset_password",
            "title": "Password updated successfully",
        }
        thread = threading.Thread(target=send_email, kwargs=context)
        thread.start()
        return attrs


class RefreshTokenSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        token = attrs.get("refresh")
        payload = SimpleToken.validate_token(token, TokenType.REFRESH.value)
        token_obj = payload.get("token_obj")
        user = token_obj.user
        token_obj.hard_delete()
        return user.auth_tokens()


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(
        max_length=255, style={"input-type": "password"}, write_only=True
    )
    new_password = serializers.CharField(
        max_length=255, style={"input-type": "password"}, write_only=True
    )

    def validate(self, attrs):
        user = self.context["request"].user
        if not user.check_password(attrs["old_password"]):
            raise serializers.ValidationError(
                {"old_password": "Old password is not correct"}
            )
        if not re.search(settings.PASSWORD_VALIDATE_REGEX, attrs["new_password"]):
            raise serializers.ValidationError(settings.PASSWORD_VALIDATE_STRING)
        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        user.set_password(validated_data["new_password"])
        user.save()
        return user


class ResendVerificationEmailSerializer(BaseSerializer):
    email = serializers.EmailField(max_length=255)

    class Meta:
        model = User
        fields = ["email"]

    def validate(self, attrs):
        email = attrs.get("email").lower()
        user = User.objects.filter(email=email)
        if user.exists():
            user = user.first()
            Token.objects.filter(user=user, token_type="verify_mail").delete()
            token = SimpleToken.for_user(
                user,
                TokenType.VERIFY_MAIL.value,
                settings.AUTH_VERIFY_EMAIL_TOKEN_LIFELINE,
            )
            context = {
                "subject": "Verify Your E-mail Address!",
                "user": user,
                "recipients": [user.email],
                "button_links": [f"{settings.HOST_URL}/api/auth/verify-email/{token}"],
                "html_template": "verify_email",
                "title": "Verify Your E-mail Address",
            }
            thread = threading.Thread(target=send_email, kwargs=context)
            thread.start()
        else:
            logger.error(f"Resend verification mail sent fail due to {email} not found")
        return attrs


class VerifyEmailSerializer(BaseSerializer):
    token = serializers.CharField()

    class Meta:
        model = User
        fields = ["token"]

    def validate_token(self, value):
        payload = SimpleToken.decode(value)
        payload = SimpleToken.validate_token(value, TokenType.VERIFY_MAIL.value)
        token_obj = payload.get("token_obj")
        user = token_obj.user
        user.is_active = True
        user.save()
        token_obj.hard_delete()
        return value


class LogoutSerializer(serializers.Serializer):
    def validate(self, attrs):
        jti = self.context["request"].auth["jti"]
        Token.default.filter(jti=jti, user=self.context["request"].user).delete()
        return attrs


class GoogleSSOSerializer(BaseSerializer):
    authorization_code = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ["authorization_code"]

    def validate(self, attrs):
        authorization_code = attrs.get("authorization_code")
        google = Google()
        data = google.validate_google_token(authorization_code)
        email = data.get("email")
        first_name = data.get("name")
        google_refresh_token = data.get("refresh_token")
        user = User.objects.filter(email=email)
        if user.exists():
            # Login Flow
            user = user.first()
            if user.auth_provider == "google":
                authorized_user = authenticate(email=email, password="p@$$w0Rd")
                if authorized_user:
                    user_data = user.auth_tokens()
                    return {"message": "Login done successfully!", "data": user_data}
            else:
                raise AuthenticationFailed(
                    f"Please continue your login using {user.auth_provider}"
                )
        else:
            # Register Flow
            user = {"email": email, "password": "p@$$w0Rd", "first_name": first_name}
            user = User.objects.create_user(**user)
            user.auth_provider = "google"
            user.is_active = True
            user.save()
            # new_user = authenticate(email=email, password="p@$$w0Rd")
            if user:
                user_data = user.auth_tokens()
                SimpleToken.for_user(
                    user, TokenType.GOOGLE.value, None, jti=google_refresh_token
                )
                return {"message": "Login done successfully!", "data": user_data}
            else:
                logger.error(
                    f"Google SSO failed for {email} after user creation due to authentication failed"
                )
                raise AuthenticationFailed("Authentication failed after user creation.")
                raise AuthenticationFailed("Authentication failed after user creation.")
