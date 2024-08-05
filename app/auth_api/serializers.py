from rest_framework import serializers
from auth_api.models import User, Token, BlacklistToken
from django.contrib.auth.hashers import make_password
import jwt
import re
from proj import settings

from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from utils.email import send_email
from utils.tokens import create_token, decode_token, delete_token


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    reset_token = RefreshToken.for_user(user)
    verify_token = RefreshToken.for_user(user)
    reset_token["token_type"] = "reset"
    verify_token["token_type"] = "verify"
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
        "reset": str(reset_token),
        "verify": str(verify_token),
    }


def check_blacklist(jti) -> None:
    if BlacklistToken.objects.filter(jti=jti).exists():
        raise serializers.ValidationError("Token is blacklisted")


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(style={"input_type": "password"}, write_only=True)

    class Meta:
        model = User
        fields = ["email", "name", "password"]

    def validate(self, attrs):
        password = attrs.get("password")
        if not re.search(settings.PASSWORD_VALIDATE_REGEX, password):
            raise serializers.ValidationError(settings.PASSWORD_VALIDATE_STRING)
        attrs["email"] = attrs["email"].lower()
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        user.is_active = False  # User is inactive until they verify their email
        verify_token = create_token(user, "verify")
        context = {
            "subject": "Verify Your E-mail Address!",
            "user": user,
            "recipients": [user.email],
            "button_links": [
                f"{settings.HOST_URL}/api/auth/verify-email/{verify_token}/"
            ],
            "html_template": "verify_email",
            "title": "Verify Your E-mail Address",
        }
        send_email(**context)
        return user


class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)

    class Meta:
        model = User
        fields = ["email", "password"]

    def validate(self, attrs):
        email = attrs.get("email").lower()
        password = attrs.get("password")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("User is not registered.")

        # Check if the user account is active
        if not user.is_active:
            raise serializers.ValidationError(
                "Email not verified. Please check your email."
            )

        # Authenticate the user with provided credentials
        user = authenticate(email=email, password=password)
        if not user:
            raise serializers.ValidationError("Incorrect email or password.")
        attrs["user"] = user
        return attrs

    def create(self, validated_data):
        user = validated_data["user"]
        tokens = Token.objects.filter(
            user=user,
            token_type__in=["access", "refresh"],
            is_deleted=False,
        )
        for token in tokens:
            token.soft_delete()

        # Generate new tokens
        access_token = create_token(user, "access")
        refresh_token = create_token(user, "refresh")

        return {"access": access_token, "refresh": refresh_token}


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "name", "email"]


class ForgetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)

    def validate(self, attrs):
        email = attrs.get("email").lower()
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            reset_token = create_token(user, "reset")
            context = {
                "subject": "Password Reset Request",
                "user": user,
                "recipients": [email],
                "html_template": "forgot_password",
                "button_links": [
                    f"{settings.HOST_URL}/api/auth/reset-password/{reset_token}/"
                ],
                "title": "Reset your password",
            }
            send_email(**context)
        else:
            raise serializers.ValidationError("Not Registered Email")

        return attrs


class ResendResetTokenSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)

    def validate(self, attrs):
        email = attrs.get("email").lower()
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            reset_token = create_token(user, "reset")
            context = {
                "subject": "Resend Password Reset Request",
                "user": user,
                "recipients": [email],
                "html_template": "resend_reset_password",
                "button_links": [
                    f"{settings.HOST_URL}/api/auth/reset-password/{reset_token}/"
                ],
                "title": "Reset your password",
            }
            send_email(**context)
            return attrs
        else:
            raise serializers.ValidationError("Not Registered Email")


class UserPasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField(style={"input_type": "password"}, write_only=True)

    class Meta:
        fields = ["password"]

    def validate(self, attrs):
        password = attrs.get("password")
        token = self.context.get("token")
        if not re.search(settings.PASSWORD_VALIDATE_REGEX, attrs.get("password")):
            raise serializers.ValidationError(settings.PASSWORD_VALIDATE_STRING)
        try:
            # Decode the token using the correct secret and algorithm
            payload = decode_token(token)
            if payload.get("token_type") != "reset":
                raise serializers.ValidationError("Invalid reset token")
            token_object = Token.objects.get(jti=payload["jti"])
            user = token_object.user
            user.password = make_password(password)
            user.save()
            # token_object.delete()
            delete_token(token)
            context = {
                "subject": "Password updated successfully!",
                "user": user,
                "recipients": [user.email],
                "html_template": "resend_reset_password",
                "title": "Password updated successfully",
            }
            send_email(**context)
            return attrs

        except Token.DoesNotExist:
            raise serializers.ValidationError({"token": "Token not Found"})
        except User.DoesNotExist:
            raise serializers.ValidationError({"token": "User not Found"})
        except jwt.ExpiredSignatureError:
            raise serializers.ValidationError({"token": "Token has expired."})
        except jwt.InvalidTokenError:
            raise serializers.ValidationError("Invalid token")


class RefreshTokenSerializer(serializers.Serializer):
    refresh = serializers.CharField(max_length=500)

    def create(self, validated_data):
        refresh_token = validated_data["refresh"]
        payload = decode_token(refresh_token)
        user = Token.objects.get(jti=payload["jti"]).user
        # Delete the old refresh token
        delete_token(refresh_token)
        # Generate new tokens
        new_refresh_token = create_token(user, "refresh")
        return {
            "refresh": new_refresh_token,
        }


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


class SendVerificationEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)

    def validate(self, attrs):
        email = attrs.get("email").lower()
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            verify_token = create_token(user, "verify")
            context = {
                "subject": "Verify Your E-mail Address!",
                "user": user,
                "recipients": [user.email],
                "button_links": [
                    f"{settings.HOST_URL}/api/auth/verify-email/{verify_token}/"
                ],
                "html_template": "verify_email",
                "title": "Verify Your E-mail Address",
            }
            send_email(**context)
        else:
            raise serializers.ValidationError("Not Registered Email")


class VerifyEmailSerializer(serializers.Serializer):
    token = serializers.CharField()

    def validate_token(self, value):
        try:
            payload = decode_token(value)
            if payload.get("token_type") != "verify":
                raise serializers.ValidationError("Invalid verification token")
            token_object = Token.objects.get(jti=payload["jti"])
            token_object.user
        except jwt.ExpiredSignatureError:
            raise serializers.ValidationError("Verification link has expired")
        except (jwt.exceptions.DecodeError, Token.DoesNotExist, User.DoesNotExist):
            raise serializers.ValidationError("Invalid verification link")

        return value

    def create(self, validated_data):
        token = validated_data["token"]
        payload = decode_token(token)
        token_object = Token.objects.get(jti=payload["jti"])
        user = token_object.user
        if not user.is_active:
            user.is_active = True
            user.save()
            delete_token(token)
            # token_object.delete()
            return {"message": "Email verified successfully"}
        else:
            return {"message": "Email already verified"}


class LogoutSerializer(serializers.Serializer):
    def validate(self, attrs):
        token_queryset = Token.default.filter(user=self.context["request"].user)
        if token_queryset.exists():
            token_queryset.delete()
            # delete_token
            return True
        else:
            raise serializers.ValidationError("Token invalid!")
