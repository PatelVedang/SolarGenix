import logging
import random
import re
import threading

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from proj.base_serializer import BaseModelSerializer, BaseSerializer
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from utils.custom_exception import CustomValidationError
from utils.email import EmailService, send_email

from auth_api.models import SimpleToken, Token, TokenType, User

from .constants import AuthResponseConstants
from .google import Google

logger = logging.getLogger("django")


# The `UserRegistrationSerializer` class handles user registration data validation and creation,
# including checking for existing email, password validation, and sending a verification email.
class UserRegistrationSerializer(BaseModelSerializer):
    # password = serializers.CharField(style={"input_type": "password"}, write_only=True)
    email = serializers.EmailField()
    password = serializers.CharField(
        style={"input_type": "password"}, write_only=True, label="Password"
    )

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "password"]

    def validate(self, attrs):
        """
        Validates the user-provided password based on a custom regular expression pattern.

        This function checks if the password meets the criteria defined by the
        `PASSWORD_VALIDATE_REGEX` setting. If the password does not match the pattern,
        a validation error is raised with a custom error message defined by
        `PASSWORD_VALIDATE_STRING`.

        Args:
            data (dict): The data containing the password to validate.

        Returns:
            dict: The validated data if no errors are found.

        Raises:
            serializers.ValidationError: If the password does not match the custom regex pattern.
        """
        password = attrs.get("password")
        if User.objects.filter(email=attrs.get("email").lower()).exists():
            raise CustomValidationError(AuthResponseConstants.EMAIL_ALREADY_EXISTS)

        if not re.search(settings.PASSWORD_VALIDATE_REGEX, password):
            raise serializers.ValidationError(
                {"password": f"{settings.PASSWORD_VALIDATE_STRING}__custom"}
            )
        return attrs

    def create(self, validated_data):
        validated_data["email"] = validated_data["email"].lower()
        user = User.objects.create_user(**validated_data)
        user.save()
        email_service = EmailService(user)
        email_service.send_verification_email()
        return user


class UserLoginSerializer(BaseModelSerializer):
    email = serializers.EmailField(max_length=255)

    class Meta:
        model = User
        fields = ["email", "password"]

    def validate(self, attrs):
        attrs["email"] = attrs["email"].lower()
        # Authenticate the user with provided credentials
        user = authenticate(**attrs)
        if user is None:
            user = User.objects.filter(email=attrs.get("email")).first()
            if user:
                if not user.is_email_verified:
                    Token.objects.filter(user=user, token_type="verify_mail").delete()
                    email_service = EmailService(user)
                    email_service.send_verification_email()
                    return user
            raise AuthenticationFailed(AuthResponseConstants.INVALID_CREDENTIALS)

        return user


class UserProfileSerializer(BaseModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "email", "is_active"]


class ForgotPasswordSerializer(BaseSerializer):
    email = serializers.EmailField(
        max_length=255, required=True, allow_blank=False, allow_null=False
    )

    def validate(self, attrs):
        email = attrs.get("email").lower()
        user = User.objects.filter(
            email=email, is_active=True, is_deleted=False
        ).first()
        if user:
            if user.is_email_verified:
                Token.objects.filter(user=user, token_type="reset").delete()
                email_service = EmailService(user)
                email_service.send_password_reset_email(email)

            else:
                Token.objects.filter(user=user, token_type="verify_mail").delete()
                email_service = EmailService(user)
                email_service.send_verification_email()

        else:
            logger.error(f"Forgot password mail sent fail due to {email} not found")
        return attrs


class UserPasswordResetSerializer(BaseSerializer):
    password = serializers.CharField(style={"input_type": "password"}, write_only=True)
    confirm_password = serializers.CharField(
        style={"input_type": "password"}, write_only=True
    )

    def validate(self, attrs):
        password = attrs.get("password")
        confirm_password = attrs.get("confirm_password")
        token = self.context.get("token")

        if not re.search(settings.PASSWORD_VALIDATE_REGEX, attrs.get("password")):
            raise CustomValidationError(f"{settings.PASSWORD_VALIDATE_STRING}")

        if password != confirm_password:
            raise CustomValidationError(
                AuthResponseConstants.PASSWORD_CONFIRMATION_MISMATCH
            )

        payload = SimpleToken.validate_token(token, TokenType.RESET.value)
        token_obj = payload.get("token_obj")
        user = token_obj.user
        user.password = make_password(password)
        user.save()
        token_obj.hard_delete()
        email_service = EmailService(user)
        email_service.send_password_update_confirmation()
        return attrs


class RefreshTokenSerializer(TokenRefreshSerializer, BaseSerializer):
    def validate(self, attrs):
        token = attrs.get("refresh")
        print("------------------------------------------------------------")
        print(token)
        payload = SimpleToken.validate_token(token, TokenType.REFRESH.value)
        print("-----------", payload)
        token_obj = payload.get("token_obj")
        user = token_obj.user
        token_obj.hard_delete()
        return user.auth_tokens()


class ChangePasswordSerializer(BaseSerializer):
    old_password = serializers.CharField(
        max_length=255,
        style={"input-type": "password"},
        write_only=True,
    )
    new_password = serializers.CharField(
        max_length=255, style={"input-type": "password"}, write_only=True
    )

    def validate(self, attrs):
        user = self.context["request"].user
        if not user.check_password(attrs["old_password"]):
            raise CustomValidationError(AuthResponseConstants.INCORRECT_OLD_PASSWORD)
        if not re.search(settings.PASSWORD_VALIDATE_REGEX, attrs["new_password"]):
            raise CustomValidationError(f"{settings.PASSWORD_VALIDATE_STRING}")
        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        user.set_password(validated_data["new_password"])
        user.save()
        return user


class ResendVerificationEmailSerializer(BaseSerializer):
    email = serializers.EmailField(max_length=255)

    def validate(self, attrs):
        email = attrs.get("email").lower()
        user = User.objects.filter(email=email)
        if user.exists():
            user = user.first()
            Token.objects.filter(user=user, token_type="verify_mail").delete()
            email_service = EmailService(user)
            email_service.send_verification_email()
        else:
            logger.error(f"Resend verification mail sent fail due to {email} not found")
        return attrs


class VerifyEmailSerializer(BaseSerializer):
    token = serializers.CharField()

    def validate_token(self, value):
        payload = SimpleToken.decode(value)
        try:
            payload = SimpleToken.validate_token(value, TokenType.VERIFY_MAIL.value)
        except Exception:
            raise CustomValidationError(
                AuthResponseConstants.EMAIL_VERIFICATION_LINK_EXPIRED
            )
        token_obj = payload.get("token_obj")
        user = token_obj.user
        user.is_email_verified = True
        user.save()
        token_obj.hard_delete()
        return value


class LogoutSerializer(BaseSerializer):
    def validate(self, attrs):
        auth = self.context["request"].auth
        if auth:
            jti = auth["jti"]
            Token.default.filter(jti=jti, user=self.context["request"].user).delete()
        return attrs


class GoogleSSOSerializer(BaseSerializer):
    authorization_code = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        authorization_code = attrs.get("authorization_code")
        google = Google()
        data = google.validate_google_token(authorization_code)
        email = data.get("email")
        first_name = data.get("name")
        password = data.get("sub")
        google_refresh_token = data.get("refresh_token")
        user = User.objects.filter(email=email)
        if user.exists():
            # Login Flow
            user = user.first()
            if user.auth_provider == "google":
                authorized_user = authenticate(email=email, password=password)
                if authorized_user:
                    user_data = user.auth_tokens()
                    return {"message": "Login done successfully!", "data": user_data}
            else:
                raise AuthenticationFailed(
                    f"Please continue your login using {user.auth_provider}"
                )
        else:
            # Register Flow
            user = {"email": email, "password": password, "first_name": first_name}
            user = User.objects.create_user(**user)
            user.auth_provider = "google"
            user.is_active = True
            user.is_email_verified = True
            user.save()
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


class SendOTPSerializer(BaseSerializer):
    email = serializers.EmailField(
        max_length=255, required=True, allow_blank=False, allow_null=False
    )

    def validate(self, attrs):
        email = attrs.get("email").lower()
        user = User.objects.filter(email=email)
        if user.exists():
            user = user.first()
            # Delete any existing OTP tokens
            Token.objects.filter(user=user, token_type=TokenType.OTP.value).delete()

            # Generate the OTP
            otp = random.randint(1000, 9999)

            # Save the OTP in the Token model
            reset_token = SimpleToken.for_user(
                user,
                TokenType.OTP.value,
                settings.OTP_EXPIRY_MINUTE,
                str(otp),
            )
            print(reset_token.__dict__)
            self.context["otp"] = otp
            self.context["otp_expires"] = reset_token.lifetime

            # Prepare email context
            context = {
                "subject": "Your OTP Code",
                "user": user,
                "recipients": [email],
                "html_template": "otp_email_template",  # Define your OTP email template
                "otp": otp,  # Pass the OTP to the email template
                "title": "Your One-Time Password (OTP)",
            }

            # Send the email in a separate thread
            thread = threading.Thread(target=send_email, kwargs=context)
            thread.start()
        else:
            logger.error(f"OTP sending failed, user with email {email} not found")

        return attrs

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["otp_expires"] = self.context.get("otp_expires")
        data["otp"] = self.context.get("otp")
        return data


class VerifyOTPSerializer(BaseSerializer):
    email = serializers.EmailField(
        max_length=255, required=True, allow_blank=False, allow_null=False
    )
    otp = serializers.CharField(
        max_length=6, required=True, allow_blank=False, allow_null=False
    )

    def validate(self, attrs):
        email = attrs.get("email").lower()
        otp = attrs.get("otp")
        # Check if user with this email exists
        try:
            user = User.objects.get(email=email)
            print(user)
        except User.DoesNotExist:
            raise CustomValidationError("Invalid email.")

        # Get the OTP record from the Token table
        try:
            otp_obj = Token.objects.get(
                user=user, jti=otp, token_type=TokenType.OTP.value
            )
        except Token.DoesNotExist:
            raise CustomValidationError("Invalid OTP, please try with a new OTP")
        # Check if OTP is expired
        if timezone.now() >= otp_obj.expire_at:
            raise CustomValidationError("OTP has expired.")

        return attrs


class ResetPasswordOTPSerializer(BaseSerializer):
    email = serializers.EmailField(
        max_length=255, required=True, allow_blank=False, allow_null=False
    )
    otp = serializers.CharField(
        max_length=6, required=True, allow_blank=False, allow_null=False
    )
    password = serializers.CharField(style={"input_type": "password"}, write_only=True)
    confirm_password = serializers.CharField(
        style={"input_type": "password"}, write_only=True
    )

    def validate(self, attrs):
        email = attrs.get("email").lower()
        otp = attrs.get("otp")
        password = attrs.get("password")
        confirm_password = attrs.get("confirm_password")
        # Check if user with this email exists
        try:
            user = User.objects.get(email=email)
            print(user)
        except User.DoesNotExist:
            raise CustomValidationError("Invalid email.")

        # Get the OTP record from the Token table
        try:
            otp_obj = Token.objects.get(
                user=user, jti=otp, token_type=TokenType.OTP.value
            )
        except Token.DoesNotExist:
            raise CustomValidationError("Invalid OTP, please try with a new OTP")
        # Check if OTP is expired
        if timezone.now() >= otp_obj.expire_at:
            raise CustomValidationError("OTP has expired.")

        if not re.search(settings.PASSWORD_VALIDATE_REGEX, attrs.get("password")):
            raise CustomValidationError(f"{settings.PASSWORD_VALIDATE_STRING}")

        if password != confirm_password:
            raise CustomValidationError("Passwords do not match")

        user.password = make_password(password)
        user.save()
        otp_obj.hard_delete()
        context = {
            "subject": "Password updated successfully!",
            "user": user,
            "recipients": [user.email],
            "html_template": "resend_reset_password",
            "title": "Password updated successfully",
            "button_links": [f"{settings.FRONTEND_URL}/api/auth/login"],
        }
        thread = threading.Thread(target=send_email, kwargs=context)
        thread.start()
        return attrs
