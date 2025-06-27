# from utils.permissions import IsTokenValid
from core.services.token_service import TokenService

from auth_api.serializers import (
    User2FAVerifySerializer,
    UserProfileSerializer,
)


class User2FAVerifyViewService:
    """
    Service class for handling Two-Factor Authentication (2FA) verification for a user.

    Methods:
        post_execute(request):
            Validates the provided 2FA verification data using User2FAVerifySerializer.
            On successful validation, returns a dictionary containing the serialized user profile
            and authentication tokens.

    Args:
        request (Request): The HTTP request object containing 2FA verification data.

    Returns:
        dict: A dictionary with the serialized user profile and authentication tokens.

    Raises:
        ValidationError: If the provided data is invalid.
    """

    def post_execute(self, request):
        serializer = User2FAVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        response_data = {
            "user": UserProfileSerializer(user).data,
            "tokens": TokenService.auth_tokens(user),
        }

        return response_data
