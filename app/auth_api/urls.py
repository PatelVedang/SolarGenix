from django.urls import path
from auth_api.views import (
    UserLoginView,
    UserRegistrationView,
    UserProfileView,
    UserPasswordResetView,
    ResendResetTokenView,
    VerifyEmailView,
    ForgotPasswordView,
)

urlpatterns = [
    path("auth/register/", UserRegistrationView.as_view(), name="registration"),
    path("auth/login/", UserLoginView.as_view(), name="login"),
    path("auth/me/", UserProfileView.as_view(), name="profile"),
    path("auth/forgot-password/", ForgotPasswordView.as_view(), name="forgot-password"),
    path(
        "auth/reset-password/<str:token>/",
        UserPasswordResetView.as_view(),
        name="reset-password",
    ),
    path(
        "auth/resend-user-reset-token",
        ResendResetTokenView.as_view(),
        name="resend-user-reset-token",
    ),
    path(
        "auth/verify-email/<str:token>/", VerifyEmailView.as_view(), name="verify-email"
    ),
]
