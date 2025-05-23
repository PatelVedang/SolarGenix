import logging
import random
import re
import threading

from core.models import Token, TokenType, User
from core.services.google_service import Google
from core.services.token_service import TokenService
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from proj.base_serializer import BaseModelSerializer, BaseSerializer
from proj.models import generate_password  # Import the function
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from utils.custom_exception import CustomValidationError
from utils.email import EmailService, send_email

from auth_api.custom_backend import LoginOnAuthBackend

from .constants import AuthResponseConstants

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

        authenticated = LoginOnAuthBackend.authenticate(**attrs)

        if authenticated is None:
            user = User.objects.filter(email=attrs.get("email")).first()
            if user:
                if not user.is_email_verified:
                    Token.objects.filter(user=user, token_type="verify_mail").delete()
                    email_service = EmailService(user)
                    email_service.send_verification_email()
                    return user
            raise AuthenticationFailed(AuthResponseConstants.INVALID_CREDENTIALS)

        user, tokens = authenticated

        return {"user": user, "tokens": tokens}


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
        payload = TokenService.validate_token(token, TokenType.RESET.value)

        if not re.search(settings.PASSWORD_VALIDATE_REGEX, attrs.get("password")):
            raise CustomValidationError(f"{settings.PASSWORD_VALIDATE_STRING}")

        if password != confirm_password:
            raise CustomValidationError(
                AuthResponseConstants.PASSWORD_CONFIRMATION_MISMATCH
            )

        token_obj = payload.get("token_obj")
        user = token_obj.user
        user.is_default_password = False
        user.password = make_password(password)
        user.save()
        token_obj.hard_delete()
        email_service = EmailService(user)
        email_service.send_password_update_confirmation()
        return attrs


class RefreshTokenSerializer(TokenRefreshSerializer, BaseSerializer):
    def validate(self, attrs):
        token = attrs.get("refresh")
        payload = TokenService.validate_token(token, TokenType.REFRESH.value)
        token_obj = payload.get("token_obj")
        user = token_obj.user
        token_obj.hard_delete()
        return TokenService.auth_tokens(user)


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
        user.is_default_password = False
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
            raise CustomValidationError(
                f"Resend verification mail sent fail due to {email} not found"
            )
        return attrs


class VerifyEmailSerializer(BaseSerializer):
    token = serializers.CharField()

    def validate_token(self, value):
        payload = TokenService.decode(value)
        payload = TokenService.validate_token(value, TokenType.VERIFY_MAIL.value)
        token_obj = payload.get("token_obj")
        user = token_obj.user
        user.is_email_verified = True
        user.save()
        token_obj.hard_delete()
        return value


class LogoutSerializer(BaseSerializer):
    """
    Serializer to handle user logout.

    Fields:
    - token: The refresh token to be used for logout.
    - logout_all_devices: Set to 1 to logout from all devices except Oauth module, or 0 to logout only from the current device. Default is 0.
    """

    token = serializers.CharField(write_only=True, required=True)
    logout_all_devices = serializers.IntegerField(default=0)

    def validate(self, attrs):
        token = attrs.get("token")
        logout_all_devices = attrs.get("logout_all_devices", 0)

        # Validate the provided refresh token
        payload = TokenService.validate_token(token, TokenType.REFRESH.value)
        token_obj = payload.get("token_obj")
        user = token_obj.user

        # Initialize the data dictionary
        data = {"user": user}

        # If logout_all_devices is 0, delete only the current token (using its jti)
        if logout_all_devices == 0:
            data["jti"] = token_obj.jti  # Add jti to data
        Token.default.filter(**data).exclude(token_type=TokenType.GOOGLE.value).delete()

        return attrs


class GoogleSSOSerializer(BaseSerializer):
    authorization_code = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        authorization_code = attrs.get("authorization_code")
        google = Google()
        data = google.validate_google_token(authorization_code)
        email = data.get("email")
        first_name = data.get("name")
        password = generate_password()  # Use the same function
        google_refresh_token = data.get("refresh_token")
        user = User.objects.filter(email=email)
        if user.exists():
            # Login Flow
            user = user.first()
            if not user.is_active or user.is_deleted:
                raise AuthenticationFailed(
                    "This account is either inactive or has been deleted."
                )
            if user.auth_provider == "google":
                user_data = TokenService.auth_tokens(user)
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
            user.is_default_password = True
            user.save()
            if user:
                authorized_user = authenticate(email=email, password=password)
                if authorized_user:
                    user_data = TokenService.auth_tokens(user)
                    TokenService.for_user(
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
            reset_token = TokenService.for_user(
                user,
                TokenType.OTP.value,
                settings.OTP_EXPIRY_MINUTES,
                str(otp),
            )
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
            raise CustomValidationError(
                f"OTP sending failed, user with email {email} not found"
            )

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
    email = serializers.EmailField(max_length=255, required=True)
    otp = serializers.CharField(max_length=6, required=True)
    password = serializers.CharField(style={"input_type": "password"}, write_only=True)
    confirm_password = serializers.CharField(
        style={"input_type": "password"}, write_only=True
    )

    def validate(self, attrs):
        email, otp, password, confirm_password = (
            attrs.get("email").lower(),
            attrs.get("otp"),
            attrs.get("password"),
            attrs.get("confirm_password"),
        )

        # Validate user existence and OTP
        user = User.objects.filter(email=email).first()
        if not user:
            raise CustomValidationError("Invalid email.")

        otp_obj = Token.objects.filter(
            user=user, jti=otp, token_type=TokenType.OTP.value
        ).first()
        if not otp_obj or timezone.now() >= otp_obj.expire_at:
            raise CustomValidationError("Invalid or expired OTP.")

        # Validate password format and match
        if not re.search(settings.PASSWORD_VALIDATE_REGEX, password):
            raise CustomValidationError(f"{settings.PASSWORD_VALIDATE_STRING}")
        if password != confirm_password:
            raise CustomValidationError("Passwords do not match")

        # Update user password and send success email
        user.password = make_password(password)
        user.is_default_password = False
        user.save()
        otp_obj.hard_delete()

        thread = threading.Thread(
            target=send_email,
            kwargs={
                "subject": "Password updated successfully!",
                "user": user,
                "recipients": [user.email],
                "html_template": "resend_reset_password",
                "title": "Password updated successfully",
                "button_links": [f"{settings.FRONTEND_URL}/api/auth/login"],
            },
        )
        thread.start()
        return attrs
