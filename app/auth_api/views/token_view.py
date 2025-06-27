import logging

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from utils.make_response import response
from utils.swagger import apply_swagger_tags

from auth_api.constants import AuthResponseConstants

# from utils.permissions import IsTokenValid
from auth_api.serializers import (
    RefreshTokenSerializer,
)

logger = logging.getLogger("django")


@apply_swagger_tags(
    tags=["Auth"],
    method_details={
        "post": {
            "description": "Resend refresh Token ",
            "summary": "Post method for resend refresh token",
        },
    },
)
class RefreshTokenView(TokenObtainPairView):
    """
    View for handling refresh token requests.

    This view allows clients to obtain a new access token using a valid refresh token.
    It uses the `RefreshTokenSerializer` to validate the incoming data and, upon success,
    returns the new token data along with a success message.

    Methods:
        post(request):
            Validates the provided refresh token and returns a new access token if valid.

    Permissions:
        AllowAny: This endpoint is accessible to any user (authenticated or not).
    """
    permission_classes = [AllowAny]
    serializer_class = RefreshTokenSerializer

    def post(self, request):
        serializer = RefreshTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return response(
            data=serializer.validated_data,
            status_code=status.HTTP_200_OK,
            message=AuthResponseConstants.NEW_TOKEN_GENERATED,
        )
