from django.shortcuts import render
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework import viewsets
from .serializers import *
from rest_framework.decorators import action
from rest_framework import generics
from utils.make_response import response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.serializers import TokenVerifySerializer
from rest_framework.permissions import IsAuthenticated
from django.utils.decorators import method_decorator 

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    # permission_classes = [AllowAny]
        
    @swagger_auto_schema(
        tags=['Auth'],
        operation_description= "This API will provide created user record as a response.",
        operation_summary="API to create new user."
    )
    def post(self, request, *args, **kwargs):
        register_serializer = self.serializer_class(data=request.data)
        if register_serializer.is_valid(raise_exception=True):
            result = super().create(request, *args, **kwargs) 
            return response(status=True, data=result.data, status_code=status.HTTP_200_OK, message="user created successfully.")

class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer

    @swagger_auto_schema(
        tags=['Auth'],
        operation_description= "This API will provide access and refresh token as response.",
        operation_summary="Login API."
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            return response(status=True, data=serializer.validated_data, status_code=status.HTTP_200_OK, message="user login successfully.")

class RefreshTokenView(TokenObtainPairView):
    serializer_class = CustomTokenRefreshSerializer

    @swagger_auto_schema(
        tags=['Auth'],
        operation_description= "This API will provide new access and refresh token as a reponse. We will call this API when our main access token was expired. This API will take refresh token in payload.",
        operation_summary="Refresh Token API."
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            return response(status=True, data=serializer.validated_data, status_code=status.HTTP_200_OK, message="user login successfully.")

class VerifyTokenView(TokenObtainPairView):
    serializer_class = TokenVerifySerializer

    @swagger_auto_schema(
        tags=['Auth'],
        operation_description= "This API will verify existing token. This API will take refresh/access token in payload.",
        operation_summary="Verify Token API."
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            return response(status=True, data={}, status_code=status.HTTP_200_OK, message="token verified successfully.")

class ForgotPasswordView(generics.CreateAPIView):
    serializer_class = ForgotPasswordSerializer

    @swagger_auto_schema(
        tags=['Auth'],
        operation_description= "This API takes the email address of the user as input and sends an OTP to the user's email address.",
        operation_summary="formgot Password API."
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            user = User.objects.get(email=serializer.validated_data["email"])
            return response(status=True, data={'success': True, 'otp': int(user.otp), 'expire_time': user.otp_expires}, status_code=status.HTTP_200_OK, message="successfully sent an OTP in mail. Please check your inbox.")


class ValidateOTPView(generics.GenericAPIView):
    serializer_class = OTPValidateSerializer

    @swagger_auto_schema(
        tags=['Auth'],
        operation_description=" The API will verify the OTP against the user's email address and then allow the user to reset their password.",
        operation_summary="Verify OTP API."
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        if serializer.is_valid(raise_exception=True):
            return response(status=True, data={}, status_code=status.HTTP_200_OK, message="OTP has successfully validated.")
        


class ResetPasswordView(generics.GenericAPIView):
    serializer_class = ResetPasswordSerializer

    @swagger_auto_schema(
        tags=['Auth'],
        operation_description="This API allows users to reset their password. It requires the user to submit both a new password and a confirmation of the new password in the payload. Upon successful submission, the user's password is reset.",
        operation_summary="Reset Password API"
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data,context={'request':request})
        
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return response(status=True, data={}, status_code=status.HTTP_200_OK, message="successful changing of the password.")


@method_decorator(name='get', decorator=swagger_auto_schema(
    tags=['Users'],
    operation_description="The Retrieve user profile API is an API that allows users to access their profile information.",
    operation_summary="Retrieve user profile API."
))
@method_decorator(name='put', decorator=swagger_auto_schema(auto_schema=None))
@method_decorator(name='patch', decorator=swagger_auto_schema(
    tags=['Users'],
    operation_description="The update profile API can be used to update a profile’s information in a given database.",
    operation_summary="Update user profile API."
))
class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UpdateProfileSerializer
    # queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        instance = self.request.user
        serializer = self.get_serializer(instance)
        return response(status=True, data=serializer.data, status_code=status.HTTP_200_OK, message="profile found successfully.")

    def patch(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.request.user
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return response(status=True, data=serializer.data, status_code=status.HTTP_200_OK, message="profile updated successfully.")
