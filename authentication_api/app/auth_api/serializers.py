import logging
import random
import re
from datetime import datetime, timedelta
from datetime import timezone as dt_timezone

from core.models import AUTH_PROVIDER, Token, TokenType, User
from core.services.token_service import TokenService
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import Group
from django.db import transaction
from django.utils import timezone
from proj.base_serializer import BaseModelSerializer, BaseSerializer
from proj.models import generate_password  # Import the function
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from utils.custom_exception import CustomValidationError

from auth_api.constants import AuthResponseConstants
from auth_api.custom_backend import LoginOnAuthBackend
from utils.sms import SMSService

logger = logging.getLogger("django")


# The `UserRegistrationSerializer` class handles user registration data validation and creation,
# including checking for existing email, password validation, and sending a verification email.
class UserRegistrationSerializer(BaseModelSerializer):
    """Serializer for user registration.

    This serializer handles the validation and creation of new user accounts.
    It ensures that the provided email is unique (case-insensitive) and that the password
    meets the requirements defined by a custom regular expression pattern specified in the
    Django settings. Upon successful registration, it also sends a verification email to the user.

    Fields:
        email (EmailField): The user's email address.
        first_name (CharField): The user's first name.
        last_name (CharField): The user's last name.
        password (CharField): The user's password (write-only).

    Methods:
        validate(attrs):
            Validates the email for uniqueness and the password against a custom regex pattern.
            Raises a validation error if the email already exists or the password does not meet
            the required criteria.

        create(validated_data):
            Creates a new user with the validated data, converts the email to lowercase,
            and sends a verification email to the user.
    """

    # password = serializers.CharField(style={"input_type": "password"}, write_only=True)
    email = serializers.EmailField()
    password = serializers.CharField(
        style={"input_type": "password"}, write_only=True, label="Password"
    )

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "password", "phone_number"]
        extra_kwargs = {"phone_number": {"required": True}}

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

        # Convert email to lowercase for consistency and check for existing email
        if User.objects.filter(email=attrs.get("email").lower()).exists():
            raise CustomValidationError(AuthResponseConstants.EMAIL_ALREADY_EXISTS)

        # Check for existing phone number
        if User.objects.filter(phone_number=attrs.get("phone_number")).exists():
            raise CustomValidationError("User with this phone number already exists.")

        # Validate the password against the custom regex
        if not re.search(settings.PASSWORD_VALIDATE_REGEX, password):
            raise serializers.ValidationError(
                {"password": f"{settings.PASSWORD_VALIDATE_STRING}__custom"}
            )

        return attrs

    def create(self, validated_data):
        validated_data["email"] = validated_data["email"].lower()
        user = User.objects.create_user(**validated_data)
        user.save()

        return user


class UserLoginSerializer(BaseModelSerializer):
    """
    Serializer for handling user login authentication.

    Fields:
        email (EmailField): The user's email address.
        password (CharField): The user's password (write-only).

    Meta:
        model (User): The User model associated with this serializer.
        fields (list): List of fields to be serialized ("email", "password").

    Methods:
        validate(attrs):
            Authenticates the user using the provided email and password.
            - Converts the email to lowercase.
            - Uses a custom authentication backend to verify credentials.
            - If authentication fails and the user exists but email is unverified:
                - Deletes any existing verification tokens.
                - Sends a new verification email.
                - Raises an AuthenticationFailed exception for unverified email.
            - If authentication fails for other reasons, raises an AuthenticationFailed exception for invalid credentials.
            - On successful authentication, adds the user instance and authentication tokens to the validated data.

    Returns:
        dict: Validated data including the user instance and tokens on successful authentication.

    Raises:
        AuthenticationFailed: If credentials are invalid or email is unverified.
    """

    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "password"]

    def validate(self, attrs):
        # Authenticate the user with provided credentials\
        email = attrs.pop("email", "").lower()
        password = attrs.pop("password", "")

        # Send Credintials to the custom authentication backend
        authenticated = LoginOnAuthBackend.authenticate(email=email, password=password)

        # If authentication fails, authenticated will be None
        if authenticated is None:
            user = User.objects.filter(email=email).first()
            if user:
                pass
            raise AuthenticationFailed(AuthResponseConstants.INVALID_CREDENTIALS)

        user, tokens = authenticated

        # Return the actual user instance along with the serialized data
        attrs["user"] = user
        attrs["tokens"] = tokens

        return attrs


class UserProfileSerializer(BaseModelSerializer):
    """
    Serializer for the User model, providing basic user profile information.

    Fields:
        id (int): Unique identifier for the user.
        first_name (str): User's first name.
        last_name (str): User's last name.
        email (str): User's email address.
        is_active (bool): Indicates whether the user account is active.
    """

    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "email", "is_active", "phone_number"]




class RefreshTokenSerializer(TokenRefreshSerializer, BaseSerializer):
    """
    Serializer for handling refresh token validation and renewal.

    Inherits from:
        TokenRefreshSerializer: Handles standard token refresh logic.
        BaseSerializer: Provides base serializer functionality.

    Methods:
        validate(attrs):
            Validates the provided refresh token, deletes the used token object,
            and returns new authentication tokens for the associated user.

    Args:
        attrs (dict): Dictionary containing the 'refresh' token.

    Returns:
        dict: New authentication tokens for the user.

    Raises:
        ValidationError: If the refresh token is invalid or expired.
    """

    def validate(self, attrs):
        token = attrs.get("refresh")
        payload = TokenService.validate_token(token, TokenType.REFRESH.value)
        token_obj = payload.get("token_obj")
        user = token_obj.user
        token_obj.hard_delete()
        return TokenService.auth_tokens(user)


class ChangePasswordSerializer(BaseSerializer):
    """
    Serializer for handling user password change requests.

    Fields:
        old_password (CharField): The user's current password. Write-only.
        new_password (CharField): The new password to set. Write-only.

    Methods:
        validate(attrs):
            Validates that the old password is correct and the new password meets strength requirements.
            Raises:
                CustomValidationError: If the old password is incorrect.
                serializers.ValidationError: If the new password does not meet the required regex pattern.

        create(validated_data):
            Sets the new password for the user, marks the password as non-default, and saves the user instance.

    Context:
        Expects 'request' in serializer context to access the current user.
    """

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

        # check old user password
        if not user.check_password(attrs["old_password"]):
            raise CustomValidationError(AuthResponseConstants.INCORRECT_OLD_PASSWORD)

        # check new password strength using regex
        if not re.search(settings.PASSWORD_VALIDATE_REGEX, attrs["new_password"]):
            raise serializers.ValidationError(
                {"new_password": f"{settings.PASSWORD_VALIDATE_STRING}__custom"}
            )
        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        user.set_password(validated_data["new_password"])
        user.is_default_password = False
        user.save()
        return user




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

        data = {"user": user}

        # If logout_all_devices is set to 1, delete all tokens except Google tokens
        if logout_all_devices == 0:
            data["jti"] = token_obj.jti

        Token.default.filter(**data).delete()

        return attrs




class SendOTPSerializer(BaseSerializer):
    """
    Serializer for sending OTP (One-Time Password) to a user's email address.

    Fields:
        email (EmailField): The email address of the user to send the OTP to.

    Methods:
        validate(attrs):
            Validates the provided email address. If the user exists and is active:
                - If the user's email is verified:
                    - Deletes any existing OTP tokens for the user.
                    - Generates a new OTP and saves it in the Token model.
                    - Sends the OTP to the user's email.
                    - Stores the OTP and its expiration in the serializer context.
                - If the user's email is not verified:
                    - Deletes any existing email verification tokens.
                    - Sends a verification email to the user.
            Raises:
                CustomValidationError: If the user with the provided email is not found.

        to_representation(instance):
            Extends the default representation to include 'otp' and 'otp_expires' in the response data.
    """

    email = serializers.EmailField(
        max_length=255, required=True, allow_blank=False, allow_null=False
    )

    def validate(self, attrs):
        email = attrs.get("email").lower()

        user = User.objects.filter(
            email=email, is_active=True, is_deleted=False
        ).first()

        if user:
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

            # Always send via SMS to the user's registered phone number
            sms_service = SMSService()
            sms_service.send_otp(user.phone_number, otp)
            self.context["sent_to"] = "phone"
        else:
            raise CustomValidationError(
                f"OTP sending failed, user with email {email} not found"
            )

        return attrs

    def to_representation(self, instance):
        """
        Override the to_representation method to include OTP expiration and sent_to in the response."""
        data = super().to_representation(instance)
        data["otp_expires"] = self.context.get("otp_expires")
        # data["otp"] = self.context.get("otp")
        data["sent_to"] = self.context.get("sent_to")
        return data


class VerifyOTPSerializer(BaseSerializer):
    """
    Serializer for verifying OTP (One-Time Password) during authentication.

    Fields:
        email (EmailField): The user's email address. Required, must not be blank or null.
        otp (CharField): The OTP code sent to the user's email. Required, must not be blank or null.

    Validation:
        - Ensures the provided email corresponds to an existing user.
        - Checks if the provided OTP matches a valid, non-expired OTP token for the user.
        - Raises CustomValidationError for invalid email, invalid OTP, or expired OTP.

    Returns:
        attrs (dict): The validated data if all checks pass.
    """

    phone_number = serializers.CharField(
        max_length=15, required=True, allow_blank=False, allow_null=False
    )
    otp = serializers.CharField(
        max_length=6, required=True, allow_blank=False, allow_null=False
    )

    def validate(self, attrs):
        phone_number = attrs.get("phone_number")
        otp = attrs.get("otp")

        # Check if user exists
        user = User.objects.filter(phone_number=phone_number).first()

        if not user:
            raise CustomValidationError("Invalid phone number.")

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
    """
    Serializer for handling password reset via OTP.
    Fields:
        email (EmailField): The user's email address.
        otp (CharField): The one-time password sent to the user's email.
        password (CharField): The new password to set (write-only).
        confirm_password (CharField): Confirmation of the new password (write-only).
    Validation:
        - Checks if the user with the provided email exists.
        - Validates the OTP for the user and checks if it is not expired.
        - Ensures the new password matches the required format.
        - Confirms that 'password' and 'confirm_password' fields match.
    On successful validation:
        - Updates the user's password.
        - Marks the user's password as non-default.
        - Deletes the used OTP token.
        - Sends a password update confirmation email to the user.
    Raises:
        CustomValidationError: If the email is invalid or the OTP is invalid/expired.
        serializers.ValidationError: If the password format is invalid or passwords do not match.
    """

    email = serializers.EmailField(max_length=255, required=True)
    otp = serializers.CharField(max_length=6, required=True)
    password = serializers.CharField(style={"input_type": "password"}, write_only=True)
    confirm_password = serializers.CharField(
        style={"input_type": "password"}, write_only=True
    )

    def validate(self, attrs):
        email = attrs.get("email")
        otp = attrs.get("otp")
        password = attrs.get("password")
        confirm_password = attrs.get("confirm_password")

        # Validate user existence and OTP
        user = User.objects.filter(email=email.lower()).first()

        if not user:
            raise CustomValidationError("Invalid email.")

        otp_obj = Token.objects.filter(
            user=user, jti=otp, token_type=TokenType.OTP.value
        ).first()
        if not otp_obj or timezone.now() >= otp_obj.expire_at:
            raise CustomValidationError("Invalid or expired OTP.")

        # Validate password format and match
        if not re.search(settings.PASSWORD_VALIDATE_REGEX, password):
            raise serializers.ValidationError(
                {"password": f"{settings.PASSWORD_VALIDATE_STRING}__custom"}
            )
        if password != confirm_password:
            raise serializers.ValidationError(
                {
                    "confirm_password": f"{AuthResponseConstants.PASSWORD_CONFIRMATION_MISMATCH}__custom"
                }
            )

        user.password = make_password(password)
        user.is_default_password = False
        user.save()
        otp_obj.hard_delete()

        return attrs


class UserDataMigrationSerializer(serializers.ModelSerializer):
    """
    Serializer for migrating user data, excluding sensitive fields such as 'groups' and 'user_permissions'.
    This serializer is based on the User model and is intended for scenarios where user data needs to be
    transferred or exported without including permission-related information.
    """

    class Meta:
        model = User
        exclude = ["groups", "user_permissions"]  # Exclude sensitive fields


class UserMigrationSerializer(BaseModelSerializer):
    """Serializer for migrating User instances, allowing all fields to be serialized and deserialized.
    Overrides the create method to enable custom logic during user creation, such as preserving
    the hashed password from the source data. Assumes that the provided password is already hashed
    and can be safely reused when creating new User instances."""

    class Meta:
        model = User
        fields = "__all__"

    def create(self, validated_data):
        """
        Override the create method to handle specific logic if needed,
        such as preserving the hashed password from the old model.
        """
        # The password is already hashed, so we can safely reuse it.
        User.objects.create(**validated_data)





