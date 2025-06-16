from rest_framework import status
from utils.make_response import response

from auth_api.constants import AuthResponseConstants
from auth_api.serializers import CognitoSyncTokenSerializer, CreateCognitoRoleSerializer


class CognitoSyncTokensViewService:
    def post_execute(self, request):
        serializer = CognitoSyncTokenSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        user, redirect_url = serializer.save()

        return self.prepare_response(user, serializer, redirect_url)

    def prepare_response(self, user, serializer, redirect_url):
        return response(
            data={
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                },
                "tokens": {
                    "access_token": serializer.validated_data["access_token"],
                    "refresh_token": serializer.validated_data["refresh_token"],
                    "id_token": serializer.validated_data["id_token"],
                },
                "redirect_url": redirect_url,
            },
            message=AuthResponseConstants.LOGIN_SUCCESS,
            status_code=status.HTTP_200_OK,
        )


class CreateCognitoRoleAPIViewService:
    def post_execute(self, request):
        serializer = CreateCognitoRoleSerializer(data=request.data)
        if serializer.is_valid():
            try:
                group = serializer.save()
                return response(
                    data={"group_name": group.name},
                    message=f"Group '{group.name}' created successfully in both Django and Cognito.",
                    status_code=status.HTTP_201_CREATED,
                )
            except Exception as e:
                return response(
                    message=f"Failed to create group: {str(e)}",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
        return response(
            data=serializer.errors, message="Validation failed.", status_code=status.HT
        )
