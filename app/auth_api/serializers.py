import logging
import random
import re
from datetime import datetime, timedelta
from datetime import timezone as dt_timezone

from core.models import Token, TokenType, User
from core.models.auth_api.auth import AUTH_PROVIDER
from core.services.google_service import Google
from core.services.token_service import TokenService
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group
from django.db import transaction
from django.utils import timezone
from proj.base_serializer import BaseModelSerializer, BaseSerializer
from proj.models import generate_password  # Import the function
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from utils.custom_exception import CustomValidationError
from utils.email import EmailService

from auth_api.cognito import Cognito
from auth_api.constants import AuthResponseConstants
from auth_api.custom_backend import LoginOnAuthBackend
from auth_api.services.totp_service import TOTPService

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

        # Convert email to lowercase for consistency and check for existing email
        if User.objects.filter(email=attrs.get("email").lower()).exists():
            raise CustomValidationError(AuthResponseConstants.EMAIL_ALREADY_EXISTS)

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

        # Send verification email
        email_service = EmailService(user)
        email_service.send_verification_email()

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
                if not user.is_email_verified:
                    Token.objects.filter(user=user, token_type="verify_mail").delete()

                    EmailService(user).send_verification_email()
                    raise AuthenticationFailed(
                        AuthResponseConstants.LOGIN_UNVERIFIED_EMAIL
                    )
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
        fields = ["id", "first_name", "last_name", "email", "is_active"]


class ForgotPasswordSerializer(BaseSerializer):
    """
    Serializer for handling forgot password requests.

    Validates the provided email address, checks for an active and non-deleted user,
    and triggers the appropriate email (password reset or verification) based on the user's email verification status.
    If the user is not found, logs an error.

    Fields:
        email (EmailField): The email address of the user requesting password reset.

    Methods:
        validate(attrs):
            - Checks if the user exists and is active.
            - If the user's email is verified, deletes any existing reset tokens and sends a password reset email.
            - If the user's email is not verified, deletes any existing verification tokens and sends a verification email.
            - Logs an error if the user is not found.
            - Returns the validated attributes.
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
    """
    Serializer for handling user password reset functionality.

    Fields:
        password (CharField): The new password to set for the user. Write-only.
        confirm_password (CharField): Confirmation of the new password. Write-only.

    Methods:
        validate(attrs):
            Validates the provided password and confirmation, checks password strength,
            validates the reset token, updates the user's password, deletes the used token,
            and sends a password update confirmation email.

            Raises:
                serializers.ValidationError: If the password does not meet strength requirements,
                                             if the passwords do not match, or if the token is invalid.

            Returns:
                dict: The validated attributes.
    """

    password = serializers.CharField(style={"input_type": "password"}, write_only=True)
    confirm_password = serializers.CharField(
        style={"input_type": "password"}, write_only=True
    )

    def validate(self, attrs):
        password = attrs.get("password")
        confirm_password = attrs.get("confirm_password")
        token = self.context.get("token")

        # Validate the token
        payload = TokenService.validate_token(token, TokenType.RESET.value)

        # Check Paassword strength using regex
        if not re.search(settings.PASSWORD_VALIDATE_REGEX, attrs.get("password")):
            raise serializers.ValidationError(
                {"password": f"{settings.PASSWORD_VALIDATE_STRING}__custom"}
            )

        if password != confirm_password:
            raise serializers.ValidationError(
                {
                    "confirm_password": f"{AuthResponseConstants.PASSWORD_CONFIRMATION_MISMATCH}__custom"
                }
            )
        token_obj = payload.get("token_obj")
        user = token_obj.user
        user.is_default_password = False
        user.password = make_password(password)
        user.save()
        token_obj.hard_delete()  # Delete the token after successful password reset
        email_service = EmailService(user)
        email_service.send_password_update_confirmation()
        return attrs


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


class ResendVerificationEmailSerializer(BaseSerializer):
    """
    Serializer for resending verification emails to users.

    Fields:
        email (EmailField): The email address of the user requesting verification.

    Methods:
        validate(attrs):
            Validates the provided email address.
            - Converts the email to lowercase.
            - Checks if a user with the given email exists.
            - If the user exists:
                - Deletes any existing verification tokens for the user.
                - Sends a new verification email using the EmailService.
            - If the user does not exist:
                - Raises a CustomValidationError indicating the email was not found.
            - Returns the validated attributes.
    """

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
            # logger.error(f"Resend verification mail sent fail due to {email} not found")
            raise CustomValidationError(
                f"Resend verification mail sent fail due to {email} not found"
            )
        return attrs


class VerifyEmailSerializer(BaseSerializer):
    """
    Serializer for verifying a user's email address using a token.

    Fields:
        token (CharField): The verification token provided by the user.

    Methods:
        validate_token(value):
            Validates the provided token by decoding and verifying its type.
            If valid, marks the associated user's email as verified, saves the user,
            and deletes the token object. Returns the validated token value.

    Raises:
        ValidationError: If the token is invalid or expired.
    """

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
        if user.auth_provider == AUTH_PROVIDER.get("cognito"):
            Cognito.logout_user(user)
            return attrs

        data = {"user": user}

        # If logout_all_devices is set to 1, delete all tokens except Google tokens
        if logout_all_devices == 0:
            data["jti"] = token_obj.jti

        Token.default.filter(**data).exclude(token_type=TokenType.GOOGLE.value).delete()

        return attrs


class GoogleSSOSerializer(BaseSerializer):
    """
    Serializer for handling Google Single Sign-On (SSO) authentication and registration.

    This serializer validates the Google authorization code, retrieves user information from Google,
    and either logs in the user if they already exist or registers a new user if they do not.
    It supports both login and registration flows, handling user creation, authentication,
    and token generation.

    Fields:
        authorization_code (str): The authorization code received from Google OAuth2.

    Methods:
        validate(attrs):
            Validates the provided authorization code by sending it to Google for verification.
            - If the user exists and is active, logs them in and returns authentication tokens.
            - If the user does not exist, registers a new user with the information from Google,
              authenticates them, and returns authentication tokens.
            - Raises AuthenticationFailed if the account is inactive, deleted, or if authentication fails.

    Returns:
        dict: A dictionary containing a message and user/token data upon successful login or registration.

    Raises:
        AuthenticationFailed: If the account is inactive, deleted, or authentication fails.
    """

    authorization_code = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        authorization_code = attrs.get("authorization_code")
        google = Google()
        data = google.validate_google_token(
            authorization_code
        )  # send the code to Google for validation
        email = data.get("email")
        full_name = data.get("name")
        first_name, last_name = (full_name.split(" ", 1) + [""])[:2]

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
            user = {
                "email": email,
                "password": password,
                "first_name": first_name,
                "last_name": last_name,
            }
            user = User.objects.create_user(**user)
            user.auth_provider = "google"
            user.is_active = True
            user.is_email_verified = True
            user.is_default_password = True
            user.save()
            if user:
                # Use the built-in authenticate function to verify the user
                authorized_user = authenticate(email=email, password=password)
                if authorized_user:
                    user_data = TokenService.auth_tokens(user)
                    tokens = TokenService.for_user(
                        user, TokenType.GOOGLE.value, None, jti=google_refresh_token
                    )
                    response_data = {
                        "user": user_data,  # User profile data
                        "tokens": tokens,  # Access and refresh tokens
                    }
                    return {
                        "message": "Login done successfully!",
                        "data": response_data,
                    }
            else:
                # logger.error(
                #     f"Google SSO failed for {email} after user creation due to authentication failed"
                # )
                raise AuthenticationFailed(
                    f"Google SSO failed for {email} after user creation due to authentication failed"
                )


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
            if user.is_email_verified:
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

                # Send the email in a separate thread
                email_service = EmailService(user)
                email_service.send_otp(otp=otp)

            else:
                Token.objects.filter(user=user, token_type="verify_mail").delete()
                email_service = EmailService(user)
                email_service.send_verification_email()
        else:
            # logger.error(f"OTP sending failed, user with email {email} not found")
            raise CustomValidationError(
                f"OTP sending failed, user with email {email} not found"
            )

        return attrs

    def to_representation(self, instance):
        """
        Override the to_representation method to include OTP expiration and OTP in the response."""
        data = super().to_representation(instance)
        data["otp_expires"] = self.context.get("otp_expires")
        data["otp"] = self.context.get("otp")
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
            raise serializers.ValidationError(
                {"password": f"{settings.PASSWORD_VALIDATE_STRING}__custom"}
            )
        if password != confirm_password:
            raise serializers.ValidationError(
                {
                    "confirm_password": f"{AuthResponseConstants.PASSWORD_CONFIRMATION_MISMATCH}__custom"
                }
            )

        # Update user password and send success email
        user.password = make_password(password)
        user.is_default_password = False
        user.save()
        otp_obj.hard_delete()
        email_service = EmailService(user)
        email_service.send_password_update_confirmation()

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


class CognitoSyncTokenSerializer(BaseSerializer):
    """
    Serializer for synchronizing Cognito tokens and user data.

    This serializer handles the validation and processing of an authentication code
    from AWS Cognito, exchanging it for access, refresh, and ID tokens. It decodes
    the tokens to extract user information, ensures all required fields are present,
    and manages user creation or update in the local database. It also synchronizes
    user groups based on Cognito group claims and manages token storage.

    Methods:
        validate(attrs):
            Validates the provided Cognito code, exchanges it for tokens, decodes
            the tokens, and extracts user and group information. Raises
            AuthenticationFailed on error or missing data.

        save():
            Creates or updates the user in the database based on Cognito data,
            synchronizes user groups, deletes old tokens, and stores new tokens.
            Returns the user and a redirect URL.

        sync_user_groups(user, groups):
            Clears existing user groups and assigns new groups based on Cognito claims.

        get_redirect_url_for_user(user):
            Returns a redirect URL based on the user's group profile, or "/" by default.
    """

    code = serializers.CharField()

    def validate(self, attrs):
        code = attrs["code"]

        # Validate the provided code with Cognito
        try:
            tokens = Cognito.exchange_code_for_tokens(code)
        except Exception as e:
            raise AuthenticationFailed(
                f"{AuthResponseConstants.INVALID_COGNITO_TOKEN}: {str(e)}"
            )

        access_token = tokens.get("access_token")
        refresh_token = tokens.get("refresh_token")
        id_token = tokens.get("id_token")

        # Validate that all required tokens are present
        if not all([access_token, refresh_token, id_token]):
            raise AuthenticationFailed(AuthResponseConstants.MISSING_COGNITO_TOKENS)

        try:
            # Decode the tokens to extract user information
            access_payload = Cognito.decode_token(access_token)
            id_token_payload = Cognito.decode_token(id_token)
            groups = access_payload.get("cognito:groups", [])
            attrs["groups"] = groups

        except Exception as e:
            raise AuthenticationFailed(
                f"{AuthResponseConstants.INVALID_COGNITO_TOKEN}: {str(e)}"
            )

        email = id_token_payload.get("email")
        user_sub = access_payload.get("sub")

        if not email or not user_sub:
            raise AuthenticationFailed(AuthResponseConstants.MISSING_COGNITO_FIELDS)

        attrs.update(
            {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "id_token": id_token,
                "access_payload": access_payload,
                "id_token_payload": id_token_payload,
                "email": email.lower(),
                "sub": user_sub,
            }
        )
        return attrs

    def save(self):
        email = self.validated_data["email"]
        access_token = self.validated_data["access_token"]
        refresh_token = self.validated_data["refresh_token"]
        id_token = self.validated_data["id_token"]
        user_sub = self.validated_data["sub"]

        access_payload = self.validated_data["access_payload"]
        id_token_payload = self.validated_data["id_token_payload"]
        groups = self.validated_data.get("groups", [])

        with transaction.atomic():
            user = User.objects.filter(cognito_sub=user_sub).first()

            if not user:
                user = User.default.filter(email=email).first()

                if user:
                    user.cognito_sub = user_sub
                    user.auth_provider = AUTH_PROVIDER.get("cognito")
                    user.is_email_verified = True
                    user.is_deleted = False
                    user.is_active = True
                    user.save(
                        update_fields=[
                            "cognito_sub",
                            "auth_provider",
                            "is_email_verified",
                            "is_deleted",
                            "is_active",
                        ]
                    )
                else:
                    user = User.objects.create(
                        email=email,
                        cognito_sub=user_sub,
                        auth_provider=AUTH_PROVIDER.get("cognito"),
                        is_email_verified=True,
                    )

            Token.objects.filter(
                user=user,
                token_type__in=[
                    TokenType.ACCESS,
                    TokenType.REFRESH,
                    TokenType.ID_TOKEN,
                ],
            ).delete()

            self.sync_user_groups(user, groups)

            # Create new tokens for the user with the provided cognito access and refresh tokens
            Token.objects.bulk_create(
                [
                    Token(
                        user=user,
                        jti=access_payload.get("jti", access_payload.get("sub")),
                        token=access_token,
                        token_type=TokenType.ACCESS,
                        expire_at=datetime.fromtimestamp(
                            access_payload["exp"], tz=dt_timezone.utc
                        ),
                    ),
                    Token(
                        user=user,
                        jti="cognito_refresh",
                        token=refresh_token,
                        token_type=TokenType.REFRESH,
                        expire_at=timezone.now() + timedelta(days=30),
                    ),
                    Token(
                        user=user,
                        jti=id_token_payload.get("jti", id_token_payload.get("sub")),
                        token=id_token,
                        token_type=TokenType.ID_TOKEN,
                        expire_at=datetime.fromtimestamp(
                            id_token_payload["exp"], tz=dt_timezone.utc
                        ),
                    ),
                ]
            )

        redirect_url = self.get_redirect_url_for_user(user)
        return user, redirect_url

    def sync_user_groups(self, user, groups):
        user.groups.clear()
        for group_name in groups:
            group, _ = Group.objects.get_or_create(name=group_name)
            user.groups.add(group)

    def get_redirect_url_for_user(self, user):
        group = user.groups.first()
        if group and hasattr(group, "profile") and group.profile.redirect_url:
            return group.profile.redirect_url
        return "/"


class CreateCognitoRoleSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a Django Group and synchronizing it with an AWS Cognito group.

    Fields:
        name (str): The name of the group. Required.
        description (str): Optional description for the group. Write-only.
        precedence (int): Optional precedence value for the group in Cognito. Write-only.
        role_arn (str): Optional ARN of the role to associate with the group in Cognito. Write-only.

    Methods:
        create(validated_data):
            Creates or retrieves a Django Group with the specified name.
            Attempts to create a corresponding group in AWS Cognito if it does not already exist.
            Handles synchronization and error reporting between Django and Cognito.
            Rolls back the transaction and raises a ValidationError if Cognito synchronization fails.

    Raises:
        serializers.ValidationError: If group creation or synchronization with Cognito fails.
    """

    name = serializers.CharField()
    description = serializers.CharField(
        write_only=True, required=False, allow_blank=True
    )
    precedence = serializers.IntegerField(write_only=True, required=False)
    role_arn = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = Group
        fields = ["name", "description", "precedence", "role_arn"]

    def create(self, validated_data):
        name = validated_data.pop("name", None)
        description = validated_data.pop("description", "")
        precedence = validated_data.pop("precedence", 0)
        role_arn = validated_data.pop("role_arn", None)

        with transaction.atomic():
            group, created = Group.objects.get_or_create(name=name)
            cognito = Cognito()
            try:
                try:
                    cognito.get_group(group.name)
                    logger.info(
                        f"Group '{group.name}' already exists in Cognito, skipping creation."
                    )
                except Exception:
                    cognito.create_role(
                        group_name=group.name,
                        description=description,
                        precedence=precedence,
                        role_arn=role_arn,
                    )
            except Exception as e:
                transaction.set_rollback(True)
                raise serializers.ValidationError(
                    f"Failed to create or sync group in Cognito: {str(e)}"
                )

        return group


class User2FASetupSerializer(serializers.Serializer):
    """
    Serializer for initiating 2FA (Two-Factor Authentication) setup for a user.

    Fields:
        user_id (UUIDField): The UUID of the user for whom 2FA is being set up.

    Validation:
        - Ensures the user with the given ID exists.
        - Checks that the user's email is verified.
        - Stores the user instance in the serializer context for later use.

    Create:
        - Generates a TOTP (Time-based One-Time Password) secret for the user.
        - Returns a dictionary containing the QR code URL and OTP provisioning URI for 2FA setup.
    """

    user_id = serializers.UUIDField()

    def validate_user_id(self, value):
        try:
            user = User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found")

        if not user.is_email_verified:
            raise serializers.ValidationError("Email not verified")

        self.context["user"] = user  # store it for use in create()
        return value

    def create(self, validated_data):
        user = self.context["user"]
        totp_service = TOTPService(user)
        totp_service.generate_secret()
        return {
            "qr_code": totp_service.generate_qr_code_url(),
            "otp_uri": totp_service.get_provisioning_uri(),
        }


class User2FAVerifySerializer(serializers.Serializer):
    """
    Serializer for verifying a user's Two-Factor Authentication (2FA) code.

    Fields:
        user_id (UUIDField): The unique identifier of the user attempting 2FA verification.
        code (CharField): The 2FA code provided by the user (maximum length: 6).

    Validation:
        - Ensures the user with the given user_id exists.
        - Verifies the provided 2FA code using the TOTPService.
        - Raises a ValidationError if the user does not exist or if the code is invalid.
        - On success, adds the user instance to the validated data.
    """

    user_id = serializers.UUIDField()
    code = serializers.CharField(max_length=6)

    def validate(self, attrs):
        user_id = attrs.get("user_id")
        code = attrs.get("code")

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found.")

        totp_service = TOTPService(user)
        if not totp_service.verify_code(code):
            raise serializers.ValidationError("Invalid 2FA code.")

        attrs["user"] = user
        return attrs
