import logging

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from utils import custom_throttling
from utils.make_response import response
from utils.swagger import apply_swagger_tags

# from utils.permissions import IsTokenValid
from auth_api.serializers import (
    ResendVerificationEmailSerializer,
    ResetPasswordOTPSerializer,
    SendOTPSerializer,
    VerifyEmailSerializer,
    VerifyOTPSerializer,
)

logger = logging.getLogger("django")


@apply_swagger_tags(
    tags=["Auth"],
    method_details={
        "get": {
            "description": "Verify Email",
            "summary": "Get method to verify email",
        },
    },
)
class VerifyEmailView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [custom_throttling.CustomAuthThrottle]

    def get(self, request, token):
        serializer = VerifyEmailSerializer(data={"token": token})
        serializer.is_valid(raise_exception=True)
        return response(status_code=status.HTTP_204_NO_CONTENT)


@apply_swagger_tags(
    tags=["Auth"],
    method_details={
        "post": {
            "description": "Resend Verify Token ",
            "summary": "Post method for resend verify token",
        },
    },
)
class ResendVerificationEmailView(APIView):
    throttle_classes = [custom_throttling.CustomAuthThrottle]
    permission_classes = [AllowAny]
    serializer_class = ResendVerificationEmailSerializer

    def post(self, request):
        serializer = ResendVerificationEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return response(status_code=status.HTTP_204_NO_CONTENT)


@apply_swagger_tags(
    tags=["Auth"],
    method_details={
        "post": {
            "description": "Send OTP",
            "summary": "Dynamic POST method to send OTP to users",
        },
    },
)
class SendOTPView(APIView):
    throttle_classes = [custom_throttling.CustomAuthThrottle]
    serializer_class = SendOTPSerializer

    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        return response(
            data=data,
            status_code=status.HTTP_200_OK,
            message="Successfully sent an OTP in email. Please check your inbox.",
        )


@apply_swagger_tags(
    tags=["Auth"],
    method_details={
        "post": {
            "description": "Verify API for OTP",
            "summary": "Dynamic POST method for verifying & validate OTP",
        },
    },
)
class VerifyOTPView(APIView):
    serializer_class = VerifyOTPSerializer

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return response(status_code=status.HTTP_204_NO_CONTENT)


@apply_swagger_tags(
    tags=["Auth"],
    method_details={
        "post": {
            "description": "Reset Password using OTP",
            "summary": "Post method for reset password using",
        },
    },
)
class ResetPasswordOTP(APIView):
    serializer_class = ResetPasswordOTPSerializer

    def post(self, request):
        serializer = ResetPasswordOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return response(status_code=status.HTTP_204_NO_CONTENT)
