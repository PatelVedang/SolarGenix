import logging

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from utils.make_response import response
from utils.swagger import apply_swagger_tags

from auth_api.permissions import IsAuthenticated

# from utils.permissions import IsTokenValid
from auth_api.serializers import (
    ChangePasswordSerializer,
)

logger = logging.getLogger("django")


@apply_swagger_tags(
    tags=["Auth"],
    method_details={
        "post": {
            "description": "Change password",
            "summary": "Post method for change password",
        },
    },
)
class ChangePasswordView(APIView):
    """
    API view for handling user password change requests.

    This view allows authenticated users to change their password by submitting the required data.
    It uses the `ChangePasswordSerializer` to validate and process the password change.

    Methods:
        post(request):
            Handles POST requests to change the user's password.
            Expects the request data to contain the necessary fields as defined in the serializer.
            Returns HTTP 204 No Content on successful password change.

    Permissions:
        Only accessible to authenticated users.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return response(status_code=status.HTTP_204_NO_CONTENT)
