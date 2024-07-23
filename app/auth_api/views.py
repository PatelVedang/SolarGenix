from django.shortcuts import render
from rest_framework import status
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.views import APIView
from auth_api.serializers import (
    UserRegistrationSerilizer,
    UserLoginSerilizer,
    UserProfileSerilizer,
    UserChangePasswordSerializer,
    SendPasswordResetEmailSerializer,
    UserPasswordResetSerializer,
    ChangePasswordEmailSerializer,
    ResendResetTokenSerializer,
    get_tokens_for_user,
    check_blacklist,
)
from django.contrib.auth import authenticate
# from auth_api.renderers import UserRenderer
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import AuthenticationFailed
from auth_api.models import User, Token, BlacklistToken

from rest_framework_simplejwt.tokens import UntypedToken
from drf_yasg.utils import swagger_auto_schema

from django.utils import timezone
from datetime import datetime
import jwt

from django.conf import settings

   
def blacklist_token(token):
    validated_token = UntypedToken(token)
    jti = validated_token.get('jti')
    token_type = validated_token.get('token_type','unknown')
    BlacklistToken.objects.create(jti=jti, token_type=token_type)    

class UserRegistrationView(APIView):
    # renderer_classes= [UserRenderer]
    
    # def get(self, request, format=None):
    #     return render(request, 'auth_api/registration.html')
    @swagger_auto_schema(
        operation_description="POST method for user registration",
        request_body=UserRegistrationSerilizer,
    )
    def post(self,request,format=None):
        serializer=UserRegistrationSerilizer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user=serializer.save()
           
            return Response({'msg': 'Registration done! Please verify your email.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    

class UserLoginView(APIView):
    # renderer_classes= [UserRenderer]
    # def get(self, request, format=None):
    #     return render(request, 'auth_api/login.html')
    @swagger_auto_schema(
        operation_description="POST method for user login",
        request_body=UserLoginSerilizer,
    )
    def post(self,request,format=None):
        serializer=UserLoginSerilizer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            email=serializer.data.get('email')
            password=serializer.data.get('password')
            user=authenticate(email=email,password=password)
            if user is not None:
                if user.is_active:
                    
                    existing_refresh_token = Token.objects.filter(user=user, token_type='refresh').first()
                    existing_access_token = Token.objects.filter(user=user, token_type='access').first()
                    if existing_access_token and existing_refresh_token:
                        access_token = existing_access_token.token
                        refresh_token = existing_refresh_token.token
                    else:   
                        token = get_tokens_for_user(user) 
                        access_token = token['access']
                        refresh_token = token['refresh']
                        payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=["HS256"])
                        Token.objects.create(
                            user=user,
                            jti=payload['jti'],
                            token=access_token,
                            token_type='access',
                            expires_at=datetime.fromtimestamp(payload['exp'])
                        )
                        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=["HS256"])
                        # Store refresh token
                        Token.objects.create(
                            user=user,
                            jti=payload['jti'],
                            token=refresh_token,
                            token_type='refresh',
                            expires_at=datetime.fromtimestamp(payload['exp'])
                        )
                    return Response({  'access': access_token,
                            'refresh': refresh_token, 'message': 'Login done!'}, status=status.HTTP_200_OK)
                else:
                    raise AuthenticationFailed('Email not verified. Please check your email.')
            else:
                raise AuthenticationFailed('Email or password is invalid.')
            
            
            
                
class UserProfileView(APIView): 
    # renderer_classes=[UserRenderer]
    permission_classes=[IsAuthenticated]
    def post(self,request,fromat=None):
        serializer=UserProfileSerilizer(request.user)
        # if serializer.is_valid():
        return Response(serializer.data,status=status.HTTP_200_OK)
    
    
            
class UserChangePassword(APIView):
    # renderer_classes=[UserRenderer]
    @swagger_auto_schema(
        operation_description="Send email for forgat password",
        request_body=UserChangePasswordSerializer,
    )
    def post(self,request,token,fromat=None):
        serializer=UserChangePasswordSerializer(data=request.data,context={'token':token})
        if serializer.is_valid(raise_exception=True):
            return Response({'msg':'Password Change Successfully!'},status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    
    
class ChangePassowordEmailView(APIView):
    # renderer_classes=[UserRenderer]
    # def get(self,request,format=None):
    #     return render(request,'auth_api/Email.html')
    @swagger_auto_schema(
        operation_description="Send email for forgot password",
        request_body=ChangePasswordEmailSerializer,
    )
    
    def post(self,request):
        serializer = ChangePasswordEmailSerializer(data=request.data, context={"request": request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response({'message':'successful changing of the password.'},status=status.HTTP_200_OK)
    
    
    
class SendPasswordResetEmailView(APIView):
    # renderer_classes=[UserRenderer]
    # def get(self,request,format=None):
    #     return render(request,'auth_api/Email.html')
    @swagger_auto_schema(
        operation_description="Send email for reset password",
        request_body=SendPasswordResetEmailSerializer,
    )
    def post(self,request,format=None):
        
        serializer=SendPasswordResetEmailSerializer(data=request.data,context={'user':request.user})
        if serializer.is_valid(raise_exception=True):
            return Response({'message':'Reset Password link shared on your Gmail'},status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    
class ResendResetTokenView(APIView):
    # renderer_classes=[UserRenderer]
    # def get(self,request,format=None):
    #     return render(request,'auth_api/Email.html')
    @swagger_auto_schema(
        operation_description="Send email for reset password",
        request_body=ResendResetTokenSerializer,
    )
    def post(self,request,format=None):
        
        serializer=ResendResetTokenSerializer(data=request.data,context={'user':request.user})
        if serializer.is_valid(raise_exception=True):
            return Response({'message':'Resend Reset Password link shared on your Gmail'},status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    
        
class UserPasswordResetView(APIView):
    #  template_name="auth_api/reset_confirmation.html"
    #  renderer_classes=[UserRenderer]
     @swagger_auto_schema(
        operation_description="Reset Password",
        request_body=UserPasswordResetSerializer,
    )
     def post(self,request,token):
         serializer=UserPasswordResetSerializer(data=request.data,context={'token':token})
         if serializer.is_valid(raise_exception=True):
            return Response({'msg':'Password Reset Successfully'},status=status.HTTP_200_OK)
         return JsonResponse({'msg':'Password Not Reset Successfully'},status=status.HTTP_400_BAD_REQUEST)
     
     
def reset_password(request, token):
    context = {
        'token': token,
    }
    return render(request,'auth_api/reset_password_form.html',context)

class VerifyEmailView(APIView):
    def get(self, request, token):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            print("Payload", payload)
            check_blacklist(payload['jti'])
            token_object = Token.objects.get(jti=payload['jti'])
            user = token_object.user
            if not user.is_active:
                user.is_active = True
                user.save()
                # token_object.delete()
                return Response({'message': 'Email verified successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Email already verified'}, status=status.HTTP_200_OK)

        except jwt.ExpiredSignatureError:
            return Response({'error': 'Verification link has expired'}, status=status.HTTP_400_BAD_REQUEST)
        except (jwt.exceptions.DecodeError, Token.DoesNotExist, User.DoesNotExist):
            return Response({'error': 'Invalid verification link'}, status=status.HTTP_400_BAD_REQUEST)
