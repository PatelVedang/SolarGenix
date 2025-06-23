import logging

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from utils import custom_throttling
from utils.make_response import response
from utils.swagger import apply_swagger_tags

from auth_api.permissions import IsAuthenticated

# from utils.permissions import IsTokenValid
from auth_api.serializers import (
    ChangePasswordSerializer,
    ForgotPasswordSerializer,
    UserPasswordResetSerializer,
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


@apply_swagger_tags(
    tags=["Auth"],
    method_details={
        "post": {
            "description": "Forgot password",
            "summary": "Post method for forgot password",
        },
    },
)
class ForgotPasswordView(APIView):
    """
    API view to handle forgot password requests.

    This view accepts POST requests with user data (typically an email address)
    to initiate the password reset process. It uses a custom throttle class to
    limit request rates and validates input using the ForgotPasswordSerializer.

    Methods:
        post(request):
            Validates the provided data and, if valid, initiates the password
            reset process (such as sending a reset email). Returns HTTP 204 No Content
            on success.
    """

    throttle_classes = [custom_throttling.CustomAuthThrottle]
    serializer_class = ForgotPasswordSerializer

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return response(status_code=status.HTTP_204_NO_CONTENT)


@apply_swagger_tags(
    tags=["Auth"],
    method_details={
        "post": {
            "description": "Reset Password",
            "summary": "Post method for resending request to reset password",
        },
    },
)
@apply_swagger_tags(
    tags=["Auth"],
    method_details={
        "post": {
            "description": "Reset Password",
            "summary": "Post method for reset password",
        },
    },
)
class UserPasswordResetView(APIView):
    """
    API view to handle user password reset requests.

    This view allows unauthenticated users to reset their password using a provided token.
    It applies custom throttling and uses the `UserPasswordResetSerializer` to validate the request data.

    Methods:
        post(request, token): Validates the password reset data and processes the password reset.
            - Parameters:
                request (Request): The HTTP request object containing the new password data.
                token (str): The password reset token.
            - Returns:
                HTTP 204 No Content on successful password reset.
    """
    permission_classes = [AllowAny]
    throttle_classes = [custom_throttling.CustomAuthThrottle]
    serializer_class = UserPasswordResetSerializer

    def post(self, request, token):
        serializer = UserPasswordResetSerializer(
            data=request.data, context={"token": token}
        )
        serializer.is_valid(raise_exception=True)
        return response(status_code=status.HTTP_204_NO_CONTENT)
