import logging

from rest_framework import status
from rest_framework.views import APIView
from utils import custom_throttling
from utils.make_response import response
from utils.swagger import apply_swagger_tags

from auth_api.constants import AuthResponseConstants
from auth_api.permissions import IsAuthenticated
from auth_api.serializers import (
    LogoutSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    UserRegistrationSerializer,
)
from auth_api.services import UserLoginViewService, UserRegisterViewService

logger = logging.getLogger("django")


@apply_swagger_tags(
    tags=["Auth"],
    method_details={
        "post": {
            "description": "Login API with 2FA support",
            "summary": "Dynamic POST method for user login with optional 2FA step",
        },
    },
)
class UserLoginView(APIView):
    throttle_classes = [custom_throttling.CustomAuthThrottle]
    serializer_class = UserLoginSerializer
    permission_classes = []

    def post(self, request):
        service = UserLoginViewService()
        validated_data = service.post_execute(request)
        return response(
            data=validated_data,
            status_code=status.HTTP_200_OK,
            message=AuthResponseConstants.LOGIN_SUCCESS,
        )


@apply_swagger_tags(
    tags=["Auth"],
    method_details={
        "post": {
            "description": "User registration",
            "summary": "POST method for user registration",
        },
    },
)
class UserRegistrationView(APIView):
    throttle_classes = [custom_throttling.CustomAuthThrottle]
    serializer_class = UserRegistrationSerializer

    def post(self, request):
        service = UserRegisterViewService()
        response_data = service.post_execute(request)
        return response(
            data=response_data,
            status_code=status.HTTP_201_CREATED,
            message=AuthResponseConstants.REGISTRATION_SUCCESS,
        )


@apply_swagger_tags(
    tags=["Auth"],
    method_details={
        "get": {
            "description": "User profile",
            "summary": "GET method for user profile details",
        },
    },
)
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [custom_throttling.CustomAuthThrottle]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return response(
            data=serializer.data,
            status_code=status.HTTP_200_OK,
            message=AuthResponseConstants.USER_FOUND,
        )


@apply_swagger_tags(
    tags=["Auth"],
    method_details={
        "post": {
            "description": "Logout",
            "summary": "Post method for logout",
        },
    },
)
class LogoutView(APIView):
    serializer_class = LogoutSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return response(status_code=status.HTTP_204_NO_CONTENT)
