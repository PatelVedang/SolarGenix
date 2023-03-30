from django.urls import path, include
from . import views
from rest_framework import routers
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
# router = routers.DefaultRouter()
# router.register('', views.AuthViews,basename='auth')

urlpatterns = [
    path('auth/register', views.RegisterView.as_view(), name='register'),
    path('auth/login', views.LoginView.as_view(), name='login'),
    path('auth/refreshToken', views.RefreshTokenView.as_view(), name='refreshToken'),
    path('auth/verifyToken', views.VerifyTokenView.as_view(), name='verifyToken'),
    path('auth/forgotPassword', views.ForgotPasswordView.as_view(),name="forgot-password"),
    path('auth/validateOtp', views.ValidateOTPView.as_view(), name='validate-otp'),
    path('auth/resetPassword', views.ResetPasswordView.as_view(), name="reset-password"),
    path('users/profile', views.ProfileView.as_view(), name='update-profile'),
    path('users/changePassword', views.ChangePasswordView.as_view(), name='change-password')
]
