from django.urls import path

from auth_api.views import (
    ChangePasswordView,
    LogoutView,
    RefreshTokenView,
    ResetPasswordOTP,
    SendOTPView,
    UserLoginView,
    UserProfileView,
    UserRegistrationView,
    VerifyOTPView,
)

urlpatterns = [
    path("register", UserRegistrationView.as_view(), name="registration"),
    path("login", UserLoginView.as_view(), name="login"),
    path("me", UserProfileView.as_view(), name="me"),
    path(
        "change-password",
        ChangePasswordView.as_view(),
        name="change-password",
    ),
    path("refresh-token", RefreshTokenView.as_view(), name="refresh-token"),
    path("logout", LogoutView.as_view(), name="login-view"),
    path("send-otp", SendOTPView.as_view(), name="send-otp-view"),
    path("verify-otp", VerifyOTPView.as_view(), name="verify-otp-view"),
    path(
        "reset-password-otp", ResetPasswordOTP.as_view(), name="reset-password-otp"
    ),
]
