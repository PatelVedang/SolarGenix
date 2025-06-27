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
    serializer_class = GoogleSSOSerializer

    def post(self, request):
        serializer = GoogleSSOSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        message = data.get("message")
        data = data.get("data")
        return response(status_code=status.HTTP_200_OK, message=message, data=data)
