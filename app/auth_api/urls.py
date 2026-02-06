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
    path("auth/register", UserRegistrationView.as_view(), name="registration"),
    path("auth/login", UserLoginView.as_view(), name="login"),
    path("auth/me", UserProfileView.as_view(), name="me"),
    path(
        "auth/change-password",
        ChangePasswordView.as_view(),
        name="change-password",
    ),
    path("auth/refresh-token", RefreshTokenView.as_view(), name="refresh-token"),
    path("auth/logout", LogoutView.as_view(), name="login-view"),
    path("auth/send-otp", SendOTPView.as_view(), name="send-otp-view"),
    path("auth/verify-otp", VerifyOTPView.as_view(), name="verify-otp-view"),
    path(
        "auth/reset-password-otp", ResetPasswordOTP.as_view(), name="reset-password-otp"
    ),
]
