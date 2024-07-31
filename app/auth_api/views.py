from django.shortcuts import render
from rest_framework import status
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.views import APIView
from auth_api.serializers import (
    UserRegistrationSerilizer,
    UserLoginSerializer,
    UserProfileSerilizer,
    SendPasswordResetEmailSerializer,
    UserPasswordResetSerializer,
    ChangePasswordSerializer,
    ResendResetTokenSerializer,
    RefreshTokenSerializer,
    ResendVerifyTokenSerializer,
    VerifyEmailSerializer,
    LogoutSerializer,
    get_tokens_for_user,
    check_blacklist,
)
from utils.make_response import response
from utils.custom_filter import apply_filters
from django.contrib.auth import authenticate
# from auth_api.renderers import UserRenderer
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import AuthenticationFailed
from auth_api.models import User, Token, BlacklistToken
from auth_api.permissions import IsTokenValid
from rest_framework_simplejwt.tokens import UntypedToken
from drf_yasg.utils import swagger_auto_schema

from django.utils import timezone
from datetime import datetime
import jwt

from django.conf import settings
from utils.swagger import apply_swagger_tags


   
def blacklist_token(token):
    validated_token = UntypedToken(token)
    jti = validated_token.get('jti')
    token_type = validated_token.get('token_type','unknown')
    BlacklistToken.objects.create(jti=jti, token_type=token_type)    

class UserRegistrationView(APIView):
   
    @swagger_auto_schema(
        operation_description="POST method for user registration",
        request_body=UserRegistrationSerilizer,
    )
    def post(self,request):
        # select_fields = request.query_params.get('select_fields')
        # queryset = User.objects.all()
        # queryset = apply_filters(queryset,select_fields)
        serializer=UserRegistrationSerilizer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user=serializer.save()  
            return response(data=request.data, status_code=status.HTTP_201_CREATED, message="Registration Done Please  Activate Your Account!") 

        return response(status_code=status.HTTP_400_BAD_REQUEST, data=serializer.errors)


         
class UserLoginView(APIView):

    @swagger_auto_schema(
        operation_description="POST method for user login",
        request_body=UserLoginSerializer,
    )
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = authenticate(email=email, password=password)
            if user is not None:
                if user.is_active:
                    tokens = Token.objects.filter(user=user, token_type__in=['access', 'refresh'], is_deleted=False)
                    for token in tokens:
                            token.soft_delete()
                  
                    # Generate new tokens
                    token = get_tokens_for_user(user)
                    access_token = token['access']
                    refresh_token = token['refresh']

                    # Decode and store access token
                    access_payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=["HS256"])
                    Token.objects.create(
                        user=user,
                        jti=access_payload['jti'],
                        token=access_token,
                        token_type='access',
                        expires_at=datetime.fromtimestamp(access_payload['exp'])
                    )

                    # Decode and store refresh token
                    refresh_payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=["HS256"])
                    Token.objects.create(
                        user=user,
                        jti=refresh_payload['jti'],
                        token=refresh_token,
                        token_type='refresh',
                        expires_at=datetime.fromtimestamp(refresh_payload['exp'])
                    )

                    return response(data={'access': access_token, 'refresh': refresh_token}, status_code=status.HTTP_200_OK, message='Login done!')
                else:
                    raise AuthenticationFailed('Account Is Not Activated Please Activate Account')
            else:
                raise AuthenticationFailed('No active account found with the given credentials.')         
            
            
 
class UserProfileView(APIView): 
    permission_classes=[IsAuthenticated,IsTokenValid]
    
    def get(self, request):
        select_fields = request.query_params.get('select_fields')
        queryset = User.objects.all()
        
        # Apply the filter
        filtered_queryset = apply_filters(queryset, select_fields)
        
        # Serialize the filtered queryset
        serializer = UserProfileSerilizer(filtered_queryset, many=True)
        
        return response(
            data=serializer.data,
            status_code=status.HTTP_200_OK,
            message='User profiles retrieved successfully'
        )
    def post(self,request):
        select_fields = request.query_params.get('select_fields')
        queryset = User.objects.all()
        queryset = apply_filters(queryset,select_fields)
        serializer=UserProfileSerilizer(request.user,data=request.data,partial=True)
        if serializer.is_valid(raise_exception=True):
            return response(data=serializer.data,status_code=status.HTTP_200_OK,message='User Profile Created successfully')
        return response(status_code=status.HTTP_400_BAD_REQUEST, data=serializer.errors)
            

    
    
class ChangePassowordView(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_description="Send email for forgot password",
        request_body=ChangePasswordSerializer,
    )
    
    def post(self,request):
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return response(status_code=status.HTTP_204_NO_CONTENT)
    
    
    
class SendPasswordResetEmailView(APIView):
    @swagger_auto_schema(
        operation_description="Send email for reset password",
        request_body=SendPasswordResetEmailSerializer,
    )
    def post(self,request):
        
        serializer=SendPasswordResetEmailSerializer(data=request.data,context={'user':request.user})
        if serializer.is_valid(raise_exception=True):
            return response(status_code=status.HTTP_204_NO_CONTENT)      
        return response(status_code=status.HTTP_400_BAD_REQUEST, data=serializer.errors)

    
    
class ResendResetTokenView(APIView):
    @swagger_auto_schema(
        operation_description="Send email for reset password",
        request_body=ResendResetTokenSerializer,
    )
    def post(self,request):      
        serializer=ResendResetTokenSerializer(data=request.data,context={'user':request.user})
        if serializer.is_valid(raise_exception=True):
             return response(data=serializer.data,status_code=status.HTTP_200_OK,message=' Rsend Reset Password Link on Your Account') 
     
        return response(status_code=status.HTTP_400_BAD_REQUEST, data=serializer.errors)
    
        
class UserPasswordResetView(APIView):
    permission_classes=[IsTokenValid]
    @swagger_auto_schema(
        operation_description="Reset Password",
        request_body=UserPasswordResetSerializer,
    )
    def post(self,request,token):
         serializer=UserPasswordResetSerializer(data=request.data,context={'token':token})
         if serializer.is_valid(raise_exception=True):
            return response(status_code=status.HTTP_204_NO_CONTENT)
         return response(status_code=status.HTTP_400_BAD_REQUEST, data=serializer.errors)
    
     

class VerifyEmailView(APIView):
    permission_classes = [IsTokenValid]

    def get(self, request, token):
        serializer = VerifyEmailSerializer(data={'token': token})
        if serializer.is_valid():
            response_data = serializer.save()
            return response(status_code=status.HTTP_204_NO_CONTENT)
        return response(status_code=status.HTTP_400_BAD_REQUEST, data=serializer.errors)
    


class RefreshTokenView(APIView):
    @swagger_auto_schema(
        operation_description="Generate a refresh token",
        request_body=RefreshTokenSerializer,
    )
    def post(self, request):
        serializer = RefreshTokenSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            data = serializer.save()
            return response(data=data,status_code=status.HTTP_200_OK,message="Refresh token Generated")
        return response(status_code=status.HTTP_400_BAD_REQUEST, data=serializer.errors)
        
class ResendVerifyTokenView(APIView):
 
    @swagger_auto_schema(
        operation_description="Send email for Activate Account",
        request_body=ResendVerifyTokenSerializer,
    )
    def post(self,request):  
        serializer=ResendVerifyTokenSerializer(data=request.data,context={'user':request.user})
        if serializer.is_valid(raise_exception=True):
            return response(status_code=status.HTTP_204_NO_CONTENT)
        return response(status_code=status.HTTP_400_BAD_REQUEST, data=serializer.errors)
        
    
    
class LogoutView(APIView):

    serializer_class = LogoutSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(data={}, context={"request": request})
        if serializer.is_valid(raise_exception=True):
            return response(status_code=status.HTTP_204_NO_CONTENT)
