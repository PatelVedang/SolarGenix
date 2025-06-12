import logging
from django.conf import settings

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
    CognitoSyncTokenSerializer,
    CreateCognitoGroupSerializer,
    ForgotPasswordSerializer,
    GoogleSSOSerializer,
    LogoutSerializer,
    RefreshTokenSerializer,
    ResendVerificationEmailSerializer,
    ResetPasswordOTPSerializer,
    SendOTPSerializer,
    User2FASetupSerializer,
    User2FAVerifySerializer,
    UserLoginSerializer,
    UserPasswordResetSerializer,
    UserProfileSerializer,
    UserRegistrationSerializer,
    VerifyEmailSerializer,
    VerifyOTPSerializer,
)

from .constants import AuthResponseConstants
from .permissions import IsAuthenticated

logger = logging.getLogger("django")


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
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response_data = serializer.data
        return response(
            data=response_data,
            status_code=status.HTTP_201_CREATED,
            message=AuthResponseConstants.REGISTRATION_SUCCESS,
        )


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
        serializer = self.serializer_class(data=request.data)
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


        return response(
            data=validated_data,
            status_code=status.HTTP_200_OK,
            message=AuthResponseConstants.LOGIN_SUCCESS,
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
            "description": "Change password",
            "summary": "Post method for change password",
        },
    },
)
class ChangePasswordView(APIView):
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
    permission_classes = [AllowAny]
    throttle_classes = [custom_throttling.CustomAuthThrottle]
    serializer_class = UserPasswordResetSerializer

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
            "description": "Verify Email",
            "summary": "Get method to verify email",
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
            "description": "Resend refresh Token ",
            "summary": "Post method for resend refresh token",
        },
    },
)
class RefreshTokenView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = RefreshTokenSerializer

    def post(self, request):
        serializer = RefreshTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return response(
            data=serializer.validated_data,
            status_code=status.HTTP_200_OK,
            message=AuthResponseConstants.NEW_TOKEN_GENERATED,
        )


@apply_swagger_tags(
    tags=["Auth"],
    method_details={
        "post": {
            "description": "Resend Verify Token ",
            "summary": "Post method for resend verify token",
        },
    },
)
class ResendVerificationEmailView(APIView):
    throttle_classes = [custom_throttling.CustomAuthThrottle]
    permission_classes = [AllowAny]
    serializer_class = ResendVerificationEmailSerializer

    def post(self, request):
        serializer = ResendVerificationEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return response(status_code=status.HTTP_204_NO_CONTENT)


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


@apply_swagger_tags(
    tags=["Auth"],
    method_details={
        "post": {
            "description": "Google API",
            "summary": "Dynamic POST method for Google SSO",
        },
    },
)
class GoogleSSOView(APIView):
    serializer_class = GoogleSSOSerializer

    def post(self, request):
        serializer = GoogleSSOSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        message = data.get("message")
        data = data.get("data")
        return response(status_code=status.HTTP_200_OK, message=message, data=data)


@apply_swagger_tags(
    tags=["Auth"],
    method_details={
        "post": {
            "description": "Send OTP",
            "summary": "Dynamic POST method to send OTP to users",
        },
    },
)
class SendOTPView(APIView):
    throttle_classes = [custom_throttling.CustomAuthThrottle]
    serializer_class = SendOTPSerializer

    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        return response(
            data=data,
            status_code=status.HTTP_200_OK,
            message="Successfully sent an OTP in email. Please check your inbox.",
        )


@apply_swagger_tags(
    tags=["Auth"],
    method_details={
        "post": {
            "description": "Verify API for OTP",
            "summary": "Dynamic POST method for verifying & validate OTP",
        },
    },
)
class VerifyOTPView(APIView):
    serializer_class = VerifyOTPSerializer

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return response(status_code=status.HTTP_204_NO_CONTENT)


@apply_swagger_tags(
    tags=["Auth"],
    method_details={
        "post": {
            "description": "Reset Password using OTP",
            "summary": "Post method for reset password using",
        },
    },
)
class ResetPasswordOTP(APIView):
    serializer_class = ResetPasswordOTPSerializer

    def post(self, request):
        serializer = ResetPasswordOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return response(status_code=status.HTTP_204_NO_CONTENT)


@apply_swagger_tags(
    tags=["Auth"],
    method_details={
        "get": {
            "description": "Exchange Cognito code for tokens and sync user",
            "summary": "GET method for Cognito token sync using code",
        },
    },
)
class CognitoSyncTokensView(APIView):
    """
    This view is called by Cognito after user login via the hosted UI.
    It receives the `code` as a query param, exchanges it for tokens,
    manages the user and tokens, and returns the relevant data.
    """

    serializer_class = CognitoSyncTokenSerializer

    def get(self, request):
        serializer = self.serializer_class(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        user, redirect_url = serializer.save()

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


@apply_swagger_tags(
    tags=["Auth"],
    method_details={
        "post": {
            "description": "Create a new group in both Django and AWS Cognito",
            "summary": "POST method to create group in Django and sync with Cognito",
        }
    },
)
class CreateCognitoGroupAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CreateCognitoGroupSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
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
            data=serializer.errors,
            message="Validation failed.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


@apply_swagger_tags(
    tags=["Auth"],
    method_details={
        "post": {
            "description": "Setup 2FA using TOTP",
            "summary": "Generate TOTP secret and QR code for Google Authenticator",
        },
    },
)
class User2FASetupView(APIView):
    permission_classes = [AllowAny]
    serializer_class = User2FASetupSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return response(data=data, message=AuthResponseConstants.TWO_FA_SETUP_SUCCESS)


@apply_swagger_tags(
    tags=["Auth"],
    method_details={
        "post": {
            "description": "Verify 2FA TOTP code",
            "summary": "Verify TOTP code and complete login",
        },
    },
)
class User2FAVerifyView(APIView):
    throttle_classes = [custom_throttling.CustomAuthThrottle]
    serializer_class = User2FAVerifySerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        return response(
            data={
                "user": UserProfileSerializer(user).data,
                "tokens": user.auth_tokens(),
            },
            status_code=status.HTTP_200_OK,
            message=AuthResponseConstants.LOGIN_SUCCESS,
        )
