from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotAuthenticated
from rest_framework.views import APIView
from utils import custom_throttling
from utils.swagger import apply_swagger_tags
from utils.make_response import response
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
from auth_api.models import Token


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
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            response_data = {
                "email": user.email,
                "first name": user.first_name,
                "last name": user.last_name,
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
    """
    Authenticates users and generates access & refresh tokens.
    This endpoint is used for user authentication. It expects a 'email' and 'password'
    in the request body. On successful authentication, it returns access and refresh tokens.
    """

    throttle_classes = [custom_throttling.CustomAuthThrottle]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.validated_data["user"]
            # Fetch tokens for the user
            token_dict = dict(
                Token.objects.filter(
                    user=user, is_blacklisted=False, is_deleted=False
                ).values_list("token_type", "token")
            )
            return response(
                # data={"access": tokens["access"], "refresh": tokens["refresh"]},
                data={
                    "access": token_dict.get("access"),
                    "refresh": token_dict.get("refresh"),
                },
                status_code=status.HTTP_200_OK,
                message="Login done successfully!",
            )
        return response(
            status_code=status.HTTP_401_UNAUTHORIZED, data=serializer.errors
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
    permission_classes = [IsAuthenticated, IsTokenValid]
    throttle_classes = [custom_throttling.CustomAuthThrottle]

    def initial(self, request, *args, **kwargs):
        self.check_throttles(request)
        self.check_permissions(request)
        super().initial(request, *args, **kwargs)

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        if not request.user.is_authenticated:
            raise NotAuthenticated("Authentication credentials were not provided.")
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
    """
    This endpoint is used to initiate the password reset process by providing a valid email.
    The provided email should be associated with an existing user account in the system's database.
    When a valid email is provided, the user will receive an email containing a link to reset the password.
    """

    throttle_classes = [custom_throttling.CustomAuthThrottle]

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
    """
    This endpoint is used to resend a link to reset a user's password.
    The password reset process will only be completed if the password provided matches the password validation.
    Upon successful password reset, the user's password will be updated, allowing them to login using the new password.
    """

    throttle_classes = [custom_throttling.CustomAuthThrottle]

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
    throttle_classes = [custom_throttling.CustomAuthThrottle]

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
