from datetime import datetime

import jwt
from django.conf import settings
from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed

# from auth_api.renderers import UserRenderer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import UntypedToken
from utils import custom_throttling
from utils.swagger import apply_swagger_tags

from auth_api.models import BlacklistToken, Token, User
from auth_api.serializers import (
    ForgetPasswordSerializer,
    ResendResetTokenSerializer,
    UserLoginSerializer,
    UserPasswordResetSerializer,
    UserProfileSerializer,
    UserRegistrationSerializer,
    check_blacklist,
    get_tokens_for_user,
)


def blacklist_token(token):
    validated_token = UntypedToken(token)
    jti = validated_token.get("jti")
    token_type = validated_token.get("token_type", "unknown")
    BlacklistToken.objects.create(jti=jti, token_type=token_type)


# @apply_swagger_tags(tags=["Auth"])
@apply_swagger_tags(
    tags=["Auth"],
    method_details={
        "post": {
            "operation_description": "User registration",
            "request_body": UserRegistrationSerializer,
            "operation_summary": "POST method for user registration",
        },
    },
)
class UserRegistrationView(APIView):
    throttle_classes = [custom_throttling.CustomAuthThrottle]

    # def get(self, request, format=None):
    #     return render(request, 'auth_api/registration.html')
    def post(self, request, format=None):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()

            return Response(
                {"msg": "Registration done! Please verify your email."},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# @apply_swagger_tags(tags=["Auth"])
@apply_swagger_tags(
    tags=["Auth"],
    method_details={
        "post": {
            "operation_description": "Login API",
            "request_body": UserLoginSerializer,
            "operation_summary": "Dynamic POST method for user login",
        },
    },
)
class UserLoginView(APIView):
    throttle_classes = [custom_throttling.CustomAuthThrottle]

    def post(self, request, format=None):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            email = serializer.data.get("email")
            password = serializer.data.get("password")
            user = authenticate(email=email, password=password)
            if user is not None:
                if user.is_active:
                    existing_refresh_token = Token.objects.filter(
                        user=user, token_type="refresh"
                    ).first()
                    existing_access_token = Token.objects.filter(
                        user=user, token_type="access"
                    ).first()
                    if existing_access_token and existing_refresh_token:
                        access_token = existing_access_token.token
                        refresh_token = existing_refresh_token.token
                    else:
                        token = get_tokens_for_user(user)
                        access_token = token["access"]
                        refresh_token = token["refresh"]
                        payload = jwt.decode(
                            access_token, settings.SECRET_KEY, algorithms=["HS256"]
                        )
                        Token.objects.create(
                            user=user,
                            jti=payload["jti"],
                            token=access_token,
                            token_type="access",
                            expires_at=datetime.fromtimestamp(payload["exp"]),
                        )
                        payload = jwt.decode(
                            refresh_token, settings.SECRET_KEY, algorithms=["HS256"]
                        )
                        # Store refresh token
                        Token.objects.create(
                            user=user,
                            jti=payload["jti"],
                            token=refresh_token,
                            token_type="refresh",
                            expires_at=datetime.fromtimestamp(payload["exp"]),
                        )
                    return Response(
                        {
                            "access": access_token,
                            "refresh": refresh_token,
                            "message": "Login done!",
                        },
                        status=status.HTTP_200_OK,
                    )
                else:
                    raise AuthenticationFailed(
                        "Email not verified. Please check your email."
                    )
            else:
                raise AuthenticationFailed("Email or password is invalid.")


@apply_swagger_tags(
    tags=["Auth"],
    method_details={
        "post": {
            "operation_description": "User profile",
            "request_body": UserProfileSerializer,
            "operation_summary": "POST method for user profile details",
        },
    },
)
class UserProfileView(APIView):
    throttle_classes = [custom_throttling.CustomAuthThrottle]
    permission_classes = [IsAuthenticated]

    def initial(self, request, *args, **kwargs):
        self.check_throttles(request)
        self.check_permissions(request)
        super().initial(request, *args, **kwargs)

    def post(self, request, format=None):
        serializer = UserProfileSerializer(request.user)
        # if serializer.is_valid():
        return Response(serializer.data, status=status.HTTP_200_OK)


@apply_swagger_tags(
    tags=["Auth"],
    method_details={
        "post": {
            "operation_description": "Forgot password",
            "request_body": ForgetPasswordSerializer,
            "operation_summary": "Post method for forgot password",
        },
    },
)
class ForgotPasswordView(APIView):
    throttle_classes = [custom_throttling.CustomAuthThrottle]

    def post(self, request, format=None):
        serializer = ForgetPasswordSerializer(
            data=request.data, context={"user": request.user}
        )
        if serializer.is_valid(raise_exception=True):
            return Response(
                {"message": "Reset Password link shared on your Gmail"},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@apply_swagger_tags(
    tags=["Auth"],
    method_details={
        "post": {
            "operation_description": "Reset Password",
            "request_body": ResendResetTokenSerializer,
            "operation_summary": "Post method for resending request to reset password",
        },
    },
)
class ResendResetTokenView(APIView):
    throttle_classes = [custom_throttling.CustomAuthThrottle]

    def post(self, request, format=None):
        serializer = ResendResetTokenSerializer(
            data=request.data, context={"user": request.user}
        )
        if serializer.is_valid(raise_exception=True):
            return Response(
                {"message": "Resend Reset Password link shared on your Gmail"},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@apply_swagger_tags(
    tags=["Auth"],
    method_details={
        "post": {
            "operation_description": "Reset Password",
            "request_body": UserPasswordResetSerializer,
            "operation_summary": "Post method for reset password",
        },
    },
)
class UserPasswordResetView(APIView):
    throttle_classes = [custom_throttling.CustomAuthThrottle]

    def post(self, request, token):
        serializer = UserPasswordResetSerializer(
            data=request.data, context={"token": token}
        )
        if serializer.is_valid(raise_exception=True):
            return Response(
                {"msg": "Password Reset Successfully"}, status=status.HTTP_200_OK
            )
        return JsonResponse(
            {"msg": "Password Not Reset Successfully"},
            status=status.HTTP_400_BAD_REQUEST,
        )


def reset_password(request, token):
    context = {
        "token": token,
    }
    return render(request, "auth_api/reset_password_form.html", context)


@apply_swagger_tags(
    tags=["Auth"],
    method_details={
        "get": {
            "operation_description": "Verify Email",
            "operation_summary": "Get method to verify email",
        },
    },
)
class VerifyEmailView(APIView):
    throttle_classes = [custom_throttling.CustomAuthThrottle]

    def get(self, request, token):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            print("Payload", payload)
            check_blacklist(payload["jti"])
            token_object = Token.objects.get(jti=payload["jti"])
            user = token_object.user
            if not user.is_active:
                user.is_active = True
                user.save()
                return Response(
                    {"message": "Email verified successfully"},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"message": "Email already verified"}, status=status.HTTP_200_OK
                )

        except jwt.ExpiredSignatureError:
            return Response(
                {"error": "Verification link has expired"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except (jwt.exceptions.DecodeError, Token.DoesNotExist, User.DoesNotExist):
            return Response(
                {"error": "Invalid verification link"},
                status=status.HTTP_400_BAD_REQUEST,
            )
