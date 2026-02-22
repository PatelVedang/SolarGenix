import logging

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from utils.make_response import response
from utils.swagger import apply_swagger_tags

# from utils.permissions import IsTokenValid
from auth_api.serializers import (
    ResetPasswordOTPSerializer,
    SendOTPSerializer,
    VerifyOTPSerializer,
)

logger = logging.getLogger("django")


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
    """
    API view to handle sending OTP (One-Time Password) to user's email.

    This view accepts POST requests with user data, validates the input using
    SendOTPSerializer, and, upon successful validation, triggers the process
    to send an OTP to the user's email address. The response includes the
    validated data and a success message.

    Attributes:
        serializer_class (Serializer): Serializer class used for input validation.

    Methods:
        post(request):
            Handles POST requests to send an OTP to the user's email.
            Validates the request data and returns a response indicating
            the OTP has been sent.
    """
    serializer_class = SendOTPSerializer

    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        sent_to = data.get("sent_to")
        message = f"Successfully sent an OTP to your {sent_to}. Please check your {'inbox' if sent_to == 'email' else 'messages'}."
        return response(
            data=data,
            status_code=status.HTTP_200_OK,
            message=message,
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
    """
    API view for verifying OTP (One-Time Password).

    This view handles POST requests to verify an OTP provided by the user.
    It uses the `VerifyOTPSerializer` to validate the input data.
    If the data is valid, it returns a 204 No Content response.

    Methods:
        post(request):
            Validates the OTP using the serializer and returns an appropriate response.
    """

    serializer_class = VerifyOTPSerializer

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return response(
            status_code=status.HTTP_200_OK,
            message="OTP Verified Successfully",
        )


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
    """
    API view for handling password reset via OTP (One-Time Password).

    This view accepts a POST request with the required data to initiate a password reset process using an OTP.
    It validates the input using the `ResetPasswordOTPSerializer`. If the data is valid, it returns a 204 No Content response.

    Methods:
        post(request):
            Validates the request data using `ResetPasswordOTPSerializer` and returns a 204 status code on success.
    """

    serializer_class = ResetPasswordOTPSerializer

    def post(self, request):
        serializer = ResetPasswordOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return response(
            status_code=status.HTTP_200_OK,
            message="Password Reset Successfully",
        )
