# from utils.permissions import IsTokenValid
from auth_api.serializers import (
    User2FAVerifySerializer,
    UserProfileSerializer,
)


class User2FAVerifyViewService:
    def post_execute(self, request):
        serializer = User2FAVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        response_data = {
            "user": UserProfileSerializer(user).data,
            "tokens": user.auth_tokens(),
        }

        return response_data
