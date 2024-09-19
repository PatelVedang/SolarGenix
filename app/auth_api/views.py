from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from utils import custom_throttling
from utils.make_response import response
from utils.swagger import apply_swagger_tags

# from utils.permissions import IsTokenValid
from auth_api.serializers import (
    ChangePasswordSerializer,
    ForgotPasswordSerializer,
    GoogleSSOSerializer,
    LogoutSerializer,
    RefreshTokenSerializer,
    ResendResetTokenSerializer,
    ResendVerificationEmailSerializer,
    UserLoginSerializer,
    UserPasswordResetSerializer,
    UserProfileSerializer,
    UserRegistrationSerializer,
    VerifyEmailSerializer,
)

from .permissions import IsAuthenticated


@apply_swagger_tags(
    tags=["Auth"],
    method_details={
        "post": {
            "operation_description": "User registration",
            "request_body": UserRegistrationSerializer,
            "operation_summary": "POST method for user registration",
        },
    },
)
class UserRegistrationView(APIView):
    throttle_classes = [custom_throttling.CustomAuthThrottle]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response_data = serializer.data
        return response(
            data=response_data,
            status_code=status.HTTP_201_CREATED,
            message="Registration Done. Please Activate Your Account!",
        )


@apply_swagger_tags(
    tags=["Auth"],
    method_details={
        "post": {
            "operation_description": "Login API",
            "request_body": UserLoginSerializer,
            "operation_summary": "Dynamic POST method for user login",
        },
    },
)
class UserLoginView(APIView):
    throttle_classes = [custom_throttling.CustomAuthThrottle]
    permission_classes = []

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        return response(
            data=user.auth_tokens(),
            status_code=status.HTTP_200_OK,
            message="Login done successfully!",
        )


@apply_swagger_tags(
    tags=["Auth"],
    method_details={
        "get": {
            "operation_description": "User profile",
            "operation_summary": "GET method for user profile details",
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
            message="User found successfully",
        )


@apply_swagger_tags(
    tags=["Auth"],
    method_details={
        "post": {
            "operation_description": "Change password",
            "request_body": ChangePasswordSerializer,
            "operation_summary": "Post method for change password",
        },
    },
)
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

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
            "operation_description": "Forgot password",
            "request_body": ForgotPasswordSerializer,
            "operation_summary": "Post method for forgot password",
        },
    },
)
class ForgotPasswordView(APIView):
    throttle_classes = [custom_throttling.CustomAuthThrottle]

    def post(self, request):
        serializer = ForgotPasswordSerializer(
            data=request.data, context={"user": request.user}
        )
        serializer.is_valid(raise_exception=True)
        return response(status_code=status.HTTP_204_NO_CONTENT)


@apply_swagger_tags(
    tags=["Auth"],
    method_details={
        "post": {
            "operation_description": "Reset Password",
            "request_body": ResendResetTokenSerializer,
            "operation_summary": "Post method for resending request to reset password",
        },
    },
)
class ResendResetTokenView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [custom_throttling.CustomAuthThrottle]

    def post(self, request):
        serializer = ResendResetTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return response(
            data=serializer.data,
            status_code=status.HTTP_200_OK,
            message=" Reset token mail sent successfully",
        )


@apply_swagger_tags(
    tags=["Auth"],
    method_details={
        "post": {
            "operation_description": "Reset Password",
            "request_body": UserPasswordResetSerializer,
            "operation_summary": "Post method for reset password",
        },
    },
)
class UserPasswordResetView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [custom_throttling.CustomAuthThrottle]
    """
    This endpoint is used to reset a user's password.
    The password reset process will only be completed if the password provided matches the password validation .
    Upon successful password reset, the user's password will be updated, allowing them to login using the new password.
    """

    def post(self, request, token):
        serializer = UserPasswordResetSerializer(
            data=request.data, context={"token": token}
        )
        serializer.is_valid(raise_exception=True)
        return response(status_code=status.HTTP_204_NO_CONTENT)


@apply_swagger_tags(
    tags=["Auth"],
    method_details={
        "get": {
            "operation_description": "Verify Email",
            "operation_summary": "Get method to verify email",
        },
    },
)
class VerifyEmailView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [custom_throttling.CustomAuthThrottle]

    def get(self, request, token):
        serializer = VerifyEmailSerializer(data={"token": token})
        serializer.is_valid(raise_exception=True)
        return response(status_code=status.HTTP_204_NO_CONTENT)


@apply_swagger_tags(
    tags=["Auth"],
    method_details={
        "post": {
            "operation_description": "Resend Verify Token ",
            "request_body": RefreshTokenSerializer,
            "operation_summary": "Post method for resend reset token",
        },
    },
)
class RefreshTokenView(TokenObtainPairView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RefreshTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return response(
            data=serializer.validated_data,
            status_code=status.HTTP_200_OK,
            message="New token generated successfully",
        )


@apply_swagger_tags(
    tags=["Auth"],
    method_details={
        "post": {
            "operation_description": "Resend Verify Token ",
            "request_body": ResendVerificationEmailSerializer,
            "operation_summary": "Post method for resend verify token",
        },
    },
)
class ResendVerificationEmailView(APIView):
    throttle_classes = [custom_throttling.CustomAuthThrottle]
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResendVerificationEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return response(status_code=status.HTTP_204_NO_CONTENT)


@apply_swagger_tags(
    tags=["Auth"],
    method_details={
        "get": {
            "operation_description": "Logout",
            "operation_summary": "Get method for logout",
        },
    },
)
class LogoutView(APIView):
    serializer_class = LogoutSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = self.serializer_class(data={}, context={"request": request})
        serializer.is_valid(raise_exception=True)
        return response(status_code=status.HTTP_204_NO_CONTENT)


@apply_swagger_tags(
    tags=["Auth"],
    method_details={
        "post": {
            "operation_description": "Google API",
            "request_body": GoogleSSOSerializer,
            "operation_summary": "Dynamic POST method for Google SSO",
        },
    },
)
class GoogleSSOView(APIView):
    def post(self, request):
        serializer = GoogleSSOSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        message = data.get("message")
        data = data.get("data")
        return response(status_code=status.HTTP_200_OK, message=message, data=data)
