import logging
import random
import re
from datetime import datetime, timedelta
from datetime import timezone as dt_timezone

from core.models.auth_api.auth import AUTH_PROVIDER, SimpleToken
from core.models import Token, TokenType, User
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
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "password"]

    def validate(self, attrs):
        # Authenticate the user with provided credentials\
        email = attrs.pop("email", "").lower()
        password = attrs.pop("password", "")

        authenticated = LoginOnAuthBackend.authenticate(email=email, password=password)
        # If authentication fails, authenticated will be None

        if authenticated is None:
            user = User.objects.filter(email=email).first()
            if user:
                if not user.is_email_verified:
                    Token.objects.filter(user=user, token_type="verify_mail").delete()
                    email_service = EmailService(user)
                    email_service.send_verification_email()
                    raise AuthenticationFailed(
                        AuthResponseConstants.LOGIN_UNVERIFIED_EMAIL
                    )
                    return user
            raise AuthenticationFailed(AuthResponseConstants.INVALID_CREDENTIALS)

        user, tokens = authenticated
        attrs["user"] = UserProfileSerializer(user).data
        attrs["tokens"] = tokens
        return attrs


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
        try:
            token_obj = Token.objects.select_related("user").get(token=token)
        except Token.DoesNotExist:
            raise serializers.ValidationError("Invalid token")

        user = token_obj.user

        if user.auth_provider == AUTH_PROVIDER.get("cognito"):
            Cognito.logout_user(user)
            return attrs

        # For non-cognito, validate token and delete accordingly
        payload = SimpleToken.validate_token(token, TokenType.REFRESH.value)
        token_obj = payload.get(
            "token_obj"
        )  # this may be redundant if token_obj already fetched, but needed for validation

        data = {"user": user}
        if logout_all_devices == 0:
            data["jti"] = token_obj.jti

        Token.default.filter(**data).exclude(token_type=TokenType.GOOGLE.value).delete()

        return attrs


class GoogleSSOSerializer(BaseSerializer):
    authorization_code = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        authorization_code = attrs.get("authorization_code")
        google = Google()
        data = google.validate_google_token(authorization_code)
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
    class Meta:
        model = User
        exclude = ["groups", "user_permissions"]  # Exclude sensitive fields


class UserMigrationSerializer(BaseModelSerializer):
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
    code = serializers.CharField()

    def validate(self, attrs):
        code = attrs["code"]

        try:
            tokens = Cognito.exchange_code_for_tokens(code)
        except Exception as e:
            raise AuthenticationFailed(
                f"{AuthResponseConstants.INVALID_COGNITO_TOKEN}: {str(e)}"
            )

        access_token = tokens.get("access_token")
        refresh_token = tokens.get("refresh_token")
        id_token = tokens.get("id_token")

        if not all([access_token, refresh_token, id_token]):
            raise AuthenticationFailed(AuthResponseConstants.MISSING_COGNITO_TOKENS)

        try:
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


class CreateCognitoGroupSerializer(serializers.ModelSerializer):
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
                    cognito.create_group(
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
