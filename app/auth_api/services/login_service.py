from django.conf import settings
from rest_framework import status
from utils.make_response import response

from auth_api.constants import AuthResponseConstants
from auth_api.serializers import (
    UserLoginSerializer,
    UserProfileSerializer,
)


class UserLoginViewService:
    def post_execute(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        user = validated_data["user"]  # This is now a User instance

        if not user.is_email_verified:
            return response(
                data={},
                status_code=status.HTTP_200_OK,
                message=AuthResponseConstants.ACCOUNT_NOT_VERIFIED,
            )

        if settings.ENABLE_2FA:
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
