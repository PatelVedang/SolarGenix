from django.conf import settings
from rest_framework import status
from utils.make_response import response

from auth_api.constants import AuthResponseConstants
from auth_api.serializers import (
    UserLoginSerializer,
    UserProfileSerializer,
)


class UserLoginViewService:
    """
    Service class for handling user login logic.

    Methods:
        post_execute(request):
            Handles the login process for a user.
            - Validates the login data using UserLoginSerializer.
            - Checks if the user's email is verified.
            - If email is not verified, returns a response indicating the account is not verified.
            - If two-factor authentication (2FA) is enabled, returns a response indicating 2FA is required.
            - If login is successful and no further verification is needed, returns the validated user data serialized with UserProfileSerializer.

    Args:
        request (Request): The HTTP request object containing login credentials.

    Returns:
        dict or Response: Returns a response dict if email is not verified or 2FA is required, otherwise returns validated user data.
    """

    def post_execute(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        user = validated_data["user"]  # This is now a User instance

        if not user.is_email_verified:  # Check user is email verified or not
            return response(
                data={},
                status_code=status.HTTP_200_OK,
                message=AuthResponseConstants.ACCOUNT_NOT_VERIFIED,
            )

        if settings.ENABLE_2FA:    # Check if 2FA is enabled
            return response(
                data={
                    "requires_2fa": True,
                    "user_id": str(user.id),
                },
                status_code=status.HTTP_200_OK,
                message="Two-factor authentication required",
            )

        validated_data["user"] = UserProfileSerializer(user).data

        return validated_data
