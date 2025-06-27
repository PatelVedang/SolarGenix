import logging

from rest_framework import status
from rest_framework.views import APIView
from utils.make_response import response
from utils.swagger import apply_swagger_tags

# from utils.permissions import IsTokenValid
from auth_api.serializers import (
    GoogleSSOSerializer,
)

logger = logging.getLogger("django")


@apply_swagger_tags(
    tags=["Auth"],
    method_details={
        "post": {
            "description": "Google API",
            "summary": "Dynamic POST method for Google SSO",
        },
    },
)
class GoogleSSOView(APIView):
    """
    View for handling Google Single Sign-On (SSO) authentication requests.

    This view processes POST requests containing Google authentication data,
    validates the input using the `GoogleSSOSerializer`, and returns a response
    with a status code, message, and data payload.

    Methods:
        post(request):
            Handles POST requests for Google SSO authentication.
            Validates the incoming data and returns a response with the authentication result.
    """

    serializer_class = GoogleSSOSerializer

    def post(self, request):
        serializer = GoogleSSOSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        message = data.get("message")
        data = data.get("data")
        return response(status_code=status.HTTP_200_OK, message=message, data=data)
