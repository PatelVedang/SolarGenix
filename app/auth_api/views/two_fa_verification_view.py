import logging

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from utils.make_response import response
from utils.swagger import apply_swagger_tags

from auth_api.constants import AuthResponseConstants

# from utils.permissions import IsTokenValid
from auth_api.serializers import (
    User2FASetupSerializer,
    User2FAVerifySerializer,
)
from auth_api.services import User2FAVerifyViewService

logger = logging.getLogger("django")


@apply_swagger_tags(
    tags=["Auth"],
    method_details={
        "post": {
            "description": "Setup 2FA using TOTP",
            "summary": "Generate TOTP secret and QR code for Google Authenticator",
        },
    },
)
class User2FASetupView(APIView):
    """
    View for handling user 2FA (Two-Factor Authentication) setup requests.

    This view allows users to initiate the setup process for two-factor authentication.
    It accepts POST requests with the necessary data, validates the input using
    `User2FASetupSerializer`, and returns a success response upon successful setup.

    Methods:
        post(request):
            Handles POST requests to set up 2FA for a user. Validates the input data,
            saves the setup information, and returns a success message.

    Permissions:
        AllowAny: This view is accessible to any user (authenticated or not).
    """
    permission_classes = [AllowAny]
    serializer_class = User2FASetupSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return response(data=data, message=AuthResponseConstants.TWO_FA_SETUP_SUCCESS)


@apply_swagger_tags(
    tags=["Auth"],
    method_details={
        "post": {
            "description": "Verify 2FA TOTP code",
            "summary": "Verify TOTP code and complete login",
        },
    },
)
class User2FAVerifyView(APIView):
    """
    API endpoint for verifying a user's two-factor authentication (2FA) code using TOTP.

    POST:
        Verifies the provided 2FA code for a user. Expects the request data to contain the necessary
        fields as defined by the `User2FAVerifySerializer`. If verification is successful, returns
        a success response with HTTP 200 status and a login success message.

    Permissions:
        - AllowAny: This endpoint is accessible without authentication.

    Returns:
        - 200 OK: If the 2FA code is valid and verification succeeds.
        - Appropriate error response if verification fails.
    """
    serializer_class = User2FAVerifySerializer
    permission_classes = [AllowAny]

    def post(self, request):
        service = User2FAVerifyViewService()
        response_data = service.post_execute(request)

        return response(
            data=response_data,
            status_code=status.HTTP_200_OK,
            message=AuthResponseConstants.LOGIN_SUCCESS,
        )
