from rest_framework import status

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import UntypedToken
from utils.make_response import response
from utils.swagger import apply_swagger_tags

from auth_api.models import BlacklistToken
from utils.permissions import IsTokenValid
from auth_api.serializers import (
    ChangePasswordSerializer,
    ForgetPasswordSerializer,
    LogoutSerializer,
    RefreshTokenSerializer,
    ResendResetTokenSerializer,
    SendVerificationEmailSerializer,
    UserLoginSerializer,
    UserPasswordResetSerializer,
    UserProfileSerializer,
    UserRegistrationSerializer,
    VerifyEmailSerializer,
)


def blacklist_token(token):
    validated_token = UntypedToken(token)
    jti = validated_token.get("jti")
    token_type = validated_token.get("token_type", "unknown")
    BlacklistToken.objects.create(jti=jti, token_type=token_type)


# @apply_swagger_tags(tags=["Auth"])
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
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            response_data = {
                "email": user.email,
                "name": user.name,
            }
            return response(
                data=response_data,
                status_code=status.HTTP_201_CREATED,
                message="Registration Done. Please Activate Your Account!",
            )

        return response(status_code=status.HTTP_400_BAD_REQUEST, data=serializer.errors)


# @apply_swagger_tags(tags=["Auth"])
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
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            tokens = serializer.save()
            return response(
                data={"access": tokens["access"], "refresh": tokens["refresh"]},
                status_code=status.HTTP_200_OK,
                message="Login done!",
            )
        return response(
            status_code=status.HTTP_401_UNAUTHORIZED, data=serializer.errors
        )


@apply_swagger_tags(
    tags=["Auth"],
    method_details={
        "post": {
            "operation_description": "User profile",
            "request_body": UserProfileSerializer,
            "operation_summary": "POST method for user profile details",
        },
    },
)
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def post(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data)
        if serializer.is_valid(raise_exception=True):
            return response(
                data=serializer.data,
                status_code=status.HTTP_200_OK,
                message="User Profile Created successfully",
            )
        return response(status_code=status.HTTP_400_BAD_REQUEST, data=serializer.errors)


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
    permission_classes = [IsAuthenticated, IsTokenValid]

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
            "request_body": ForgetPasswordSerializer,
            "operation_summary": "Post method for forgot password",
        },
    },
)
class ForgotPasswordView(APIView):
    def post(self, request):
        serializer = ForgetPasswordSerializer(
            data=request.data, context={"user": request.user}
        )
        if serializer.is_valid(raise_exception=True):
            return response(status_code=status.HTTP_204_NO_CONTENT)
        return response(status_code=status.HTTP_400_BAD_REQUEST, data=serializer.errors)


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
    def post(self, request):
        serializer = ResendResetTokenSerializer(
            data=request.data, context={"user": request.user}
        )
        if serializer.is_valid(raise_exception=True):
            return response(
                data=serializer.data,
                status_code=status.HTTP_200_OK,
                message=" Rsend Reset Password Link on Your Account",
            )

        return response(status_code=status.HTTP_400_BAD_REQUEST, data=serializer.errors)


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
    permission_classes = [IsTokenValid]

    def post(self, request, token):
        serializer = UserPasswordResetSerializer(
            data=request.data, context={"token": token}
        )
        if serializer.is_valid(raise_exception=True):
            return response(status_code=status.HTTP_204_NO_CONTENT)
        return response(status_code=status.HTTP_400_BAD_REQUEST, data=serializer.errors)


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
    permission_classes = [IsTokenValid]

    def get(self, request, token):
        serializer = VerifyEmailSerializer(data={"token": token})
        if serializer.is_valid():
            serializer.save()
            return response(status_code=status.HTTP_204_NO_CONTENT)
        return response(status_code=status.HTTP_400_BAD_REQUEST, data=serializer.errors)


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
class RefreshTokenView(APIView):
    permission_classes = [IsTokenValid]

    def post(self, request):
        serializer = RefreshTokenSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            data = serializer.save()
            return response(
                data=data,
                status_code=status.HTTP_200_OK,
                message="Refresh token Generated",
            )
        return response(status_code=status.HTTP_400_BAD_REQUEST, data=serializer.errors)


@apply_swagger_tags(
    tags=["Auth"],
    method_details={
        "post": {
            "operation_description": "Resend Verify Token ",
            "request_body": SendVerificationEmailSerializer,
            "operation_summary": "Post method for resend verify token",
        },
    },
)
class SendVerificationEmailView(APIView):
    def post(self, request):
        serializer = SendVerificationEmailSerializer(
            data=request.data, context={"user": request.user}
        )
        if serializer.is_valid(raise_exception=True):
            return response(status_code=status.HTTP_204_NO_CONTENT)
        return response(status_code=status.HTTP_400_BAD_REQUEST, data=serializer.errors)


@apply_swagger_tags(
    tags=["Auth"],
    method_details={
        "post": {
            "operation_description": "Logout ",
            "request_body": LogoutSerializer,
            "operation_summary": "Post method for log out",
        },
    },
)
class LogoutView(APIView):
    serializer_class = LogoutSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(data={}, context={"request": request})
        if serializer.is_valid(raise_exception=True):
            return response(status_code=status.HTTP_204_NO_CONTENT)
