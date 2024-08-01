from rest_framework import serializers
from auth_api.models import User, Token, BlacklistToken
from django.contrib.auth.hashers import make_password
import jwt
import re
from datetime import datetime
from proj import settings

from auth_api.send_mail import send_email_async
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed
from utils.email import send_email


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
    password2 = serializers.CharField(style={"input_type": "password"}, write_only=True)

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

        # Generate JWT token
        tokens = get_tokens_for_user(user)
        verify_token = tokens["verify"]
        token = jwt.decode(verify_token, settings.SECRET_KEY, algorithms=["HS256"])
        Token.objects.create(
            user=user,
            jti=token["jti"],
            token=verify_token,
            token_type="verify",
            expires_at=datetime.fromtimestamp(token["exp"]),
        )
        # Send verification email
        send_email_async(
            "Verify your account",
            f"Click the link below to verify your account : {verify_token}",
            settings.EMAIL_HOST_USER,
            [user.email],
        )
        context = {
            "subject": "Verify Your E-mail Address!",
            "user": user,
            "recipients": [user.email],
            "html_template": "email-template.html",
            "button_links": [
                f"http://127.0.0.1:8000/api/auth/verify-email/{verify_token}/"
            ],
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
        attrs.get("password")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("User is not registered.")

        # Check if the user account is active
        if not user.is_active:
            raise AuthenticationFailed("Email Not Verified")
        else:
            return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "name", "email"]


class ForgetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)

    def validate(self, attrs):
        email = attrs.get("email")
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            tokens = get_tokens_for_user(user)
            reset_token = tokens["reset"]
            payload = jwt.decode(reset_token, settings.SECRET_KEY, algorithms=["HS256"])
            print("jti", payload["jti"])
            print("token type ", payload["token_type"])
            Token.objects.create(
                user=user,
                jti=payload["jti"],
                token=reset_token,
                token_type="reset",
                expires_at=datetime.fromtimestamp(payload["exp"]),
            )
            # reset_password_url = f'http://127.0.0.1:8000/api/auth/reset-password/{reset_token}/'
            context = {
                "subject": "Password Reset Request",
                "user": user,
                "recipients": [email],
                "html_template": "email-template.html",
                "button_links": [
                    f"http://127.0.0.1:8000/api/auth/reset-password/{reset_token}/"
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
        email = attrs.get("email")
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            tokens = get_tokens_for_user(user)
            reset_token = tokens["reset"]
            payload = jwt.decode(reset_token, settings.SECRET_KEY, algorithms=["HS256"])
            print("jti", payload["jti"])
            print("token type ", payload["token_type"])
            Token.objects.create(
                user=user,
                jti=payload["jti"],
                token=reset_token,
                token_type="reset",
                expires_at=datetime.fromtimestamp(payload["exp"]),
            )
            context = {
                "subject": "Resend Password Reset Request",
                "user": user,
                "recipients": [email],
                "html_template": "email-template.html",
                "button_links": [
                    f"http://127.0.0.1:8000/api/auth/reset-password/{reset_token}/"
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
        fields = ["password", "password2"]

    def validate(self, attrs):
        password = attrs.get("password")
        token = self.context.get("token")
        if not re.search(settings.PASSWORD_VALIDATE_REGEX, attrs.get("password")):
            raise serializers.ValidationError(settings.PASSWORD_VALIDATE_STRING)
        try:
            # Decode the token using the correct secret and algorithm
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            # check_blacklist(payload)
            # check_blacklist(payload['jti'])
            token_object = Token.objects.get(jti=payload["jti"])
            user = token_object.user
            user.password = make_password(password)
            user.save()
            token_object.delete()
            context = {
                "subject": "Password updated successfully!",
                "user": user,
                "recipients": [user.email],
                "html_template": "email-template.html",
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

    def validate(self, attrs):
        refresh = attrs["refresh"]
        jwt.decode(refresh, settings.SECRET_KEY, algorithms=["HS256"])
        return attrs

    def create(self, validated_data):
        refresh_token = validated_data["refresh"]
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=["HS256"])
        user = Token.objects.get(jti=payload["jti"]).user
        # user = token.user

        # Delete the old refresh token
        Token.objects.filter(user=user, token_type="refresh").delete()

        # Generate new tokens
        tokens = get_tokens_for_user(user)
        new_refresh_token = tokens["refresh"]
        new_payload = jwt.decode(
            new_refresh_token, settings.SECRET_KEY, algorithms=["HS256"]
        )

        # Save the new refresh token
        Token.objects.create(
            user=user,
            jti=new_payload["jti"],
            token=new_refresh_token,
            token_type="refresh",
            expires_at=datetime.fromtimestamp(new_payload["exp"]),
        )

        return {
            "refresh": new_refresh_token,
        }


class ResendVerifyTokenSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)

    def validate(self, attrs):
        email = attrs.get("email")
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            tokens = get_tokens_for_user(user)
            verify_token = tokens["verify"]
            payload = jwt.decode(
                verify_token, settings.SECRET_KEY, algorithms=["HS256"]
            )
            Token.objects.create(
                user=user,
                jti=payload["jti"],
                token=verify_token,
                token_type="verify",
                expires_at=datetime.fromtimestamp(payload["exp"]),
            )
            verify_url = f"http://127.0.0.1:8000/api/user/verify-email/{verify_token}"
            message = (
                f"Hello {user.name},\n\n"
                "Please Click link To activate account:\n\n"
                f"{verify_url}\n\n"
            )
            email_subject = "Activate User Account "
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [user.email]
            send_email_async(email_subject, message, email_from, recipient_list)
            return attrs
        else:
            raise serializers.ValidationError("Not Registered Email")


class VerifyEmailSerializer(serializers.Serializer):
    token = serializers.CharField()

    def validate_token(self, value):
        try:
            payload = jwt.decode(value, settings.SECRET_KEY, algorithms=["HS256"])
            check_blacklist(payload["jti"])
            token_object = Token.objects.get(jti=payload["jti"])
            token_object.user
        except jwt.ExpiredSignatureError:
            raise serializers.ValidationError("Verification link has expired")
        except (jwt.exceptions.DecodeError, Token.DoesNotExist, User.DoesNotExist):
            raise serializers.ValidationError("Invalid verification link")

        return value

    def create(self, validated_data):
        token = validated_data["token"]
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        token_object = Token.objects.get(jti=payload["jti"])
        user = token_object.user
        if not user.is_active:
            user.is_active = True
            user.save()
            # token_object.delete()
            return {"message": "Email verified successfully"}
        else:
            return {"message": "Email already verified"}


class LogoutSerializer(serializers.Serializer):
    def validate(self, attrs):
        token_queryset = Token.objects.filter(user=self.context["request"].user)
        if token_queryset.exists():
            token_queryset.delete()
            return True
        else:
            raise serializers.ValidationError("Token invalid!")
