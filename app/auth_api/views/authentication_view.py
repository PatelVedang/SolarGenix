import logging

from rest_framework import status
from rest_framework.views import APIView
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
            "description": "Login API",
            "summary": "POST method for user login",
        },
    },
)
class UserLoginView(APIView):
    """
    UserLoginView handles user authentication via POST requests.

    This view uses the UserLoginSerializer for validating login credentials. On successful 
    authentication, it returns a response with user data and a success message.

    Methods:
        post(request): Authenticates the user with provided credentials and returns a success response.
    """

    serializer_class = UserLoginSerializer
    permission_classes = []

    def post(self, request):
        service = UserLoginViewService()

        return service.post_execute(request)


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
    """
    API view for user registration.

    This view handles POST requests to register a new user. It uses the `UserRegistrationSerializer` 
    for validating input data. Upon receiving a POST request, it delegates the registration logic 
    to the `UserRegisterViewService`, and returns a response with the registration result, 
    HTTP 201 status code, and a success message.

    Methods:
        post(request): Handles user registration via POST request.
    """

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
    """
    UserProfileView handles retrieval of the authenticated user's profile information.

    Methods:
        get(request):
            Returns the serialized profile data of the currently authenticated user.

    Permissions:
        - Requires the user to be authenticated.

    Responses:
        - 200 OK: Returns the user's profile data with a success message.
    """

    permission_classes = [IsAuthenticated]

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
    """
    Handles user logout requests.

    This view accepts POST requests from authenticated users to log them out of the system.
    It uses the `LogoutSerializer` to validate the request data and requires the user to be authenticated.
    Upon successful logout, it returns a 204 No Content response.

    Methods:
        post(request): Logs out the authenticated user after validating the request data.
    """

    serializer_class = LogoutSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return response(status_code=status.HTTP_204_NO_CONTENT)
