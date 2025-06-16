import logging

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from utils import custom_throttling
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
    throttle_classes = [custom_throttling.CustomAuthThrottle]
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
