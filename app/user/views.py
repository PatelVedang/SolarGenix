import logging

from django.db.models import Q
from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework_simplejwt.views import TokenObtainPairView
from scanner.permissions import IsAuthenticated
from utils.make_response import response

from .permissions import AllowAny, AllowAnyWithoutLog, CustomIsAdminUser
from .serializers import *

logger = logging.getLogger('django')
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY
from .models import Role, User


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAnyWithoutLog]
        
    @swagger_auto_schema(
        tags=['Auth'],
        operation_description= "This API will provide created user record as a response.",
        operation_summary="API to create new user."
    )
    def post(self, request, *args, **kwargs):
        """
        A post method of a viewset. It is used to create a user.
        
        :param request: The request object
        """
        register_serializer = self.serializer_class(data=request.data)
        if register_serializer.is_valid(raise_exception=True):
            result = super().create(request, *args, **kwargs)
            return response(data=result.data, status_code=status.HTTP_200_OK, message="user created successfully.")

class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAnyWithoutLog]

    @swagger_auto_schema(
        tags=['Auth'],
        operation_description= "This API will provide access and refresh token as response.",
        operation_summary="Login API."
    )
    def post(self, request, *args, **kwargs):
        """
        It is a post method of a class. By using this method user will login into the app.
        
        :param request: The request object
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            return response(data=serializer.validated_data, status_code=status.HTTP_200_OK, message="user login successfully.")

class RefreshTokenView(TokenObtainPairView):
    serializer_class = CustomTokenRefreshSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        tags=['Auth'],
        operation_description= "This API will provide new access and refresh token as a reponse. We will call this API when our main access token was expired. This API will take refresh token in payload.",
        operation_summary="Refresh Token API."
    )
    def post(self, request, *args, **kwargs):
        """
        A function that is used to refresh the token.
        
        :param request: The request object
        :return: The response is being returned.
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            return response(data=serializer.validated_data, status_code=status.HTTP_200_OK, message="user login successfully.")

class VerifyTokenView(TokenObtainPairView):
    serializer_class = CustomTokenVerifySerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        tags=['Auth'],
        operation_description= "This API will verify existing token. This API will take refresh/access token in payload.",
        operation_summary="Verify Token API."
    )
    def post(self, request, *args, **kwargs):
        """
        A function that verifies the token.
        
        :param request: The request object
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            return response(data=serializer.validated_data, status_code=status.HTTP_200_OK, message="token verified successfully.")

class ForgotPasswordView(generics.CreateAPIView):
    serializer_class = ForgotPasswordSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        tags=['Auth'],
        operation_description= "This API takes the email address of the user as input and sends an OTP to the user's email address.",
        operation_summary="Forgot Password API."
    )
    def post(self, request):
        """
        A function which send the forgot password email to given email in request object
        
        :param request: The request object
        :return: A response object is being returned.
        """
        serializer = self.serializer_class(data=request.data, context={"request": request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            user = User.objects.get(email=serializer.validated_data["email"])
            return response(data={'success': True, 'otp': int(user.otp), 'expire_time': user.otp_expires}, status_code=status.HTTP_200_OK, message="successfully sent an OTP in mail. Please check your inbox.")


class ValidateOTPView(generics.GenericAPIView):
    serializer_class = OTPValidateSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        tags=['Auth'],
        operation_description=" The API will verify the OTP against the user's email address and then allow the user to reset their password.",
        operation_summary="Verify OTP API."
    )
    def post(self, request):
        """
        It validates the OTP.
        
        :param request: The request object
        :return: The response is being returned.
        """
        serializer = self.serializer_class(data=request.data, context={"request": request})
        if serializer.is_valid(raise_exception=True):
            return response(data={}, status_code=status.HTTP_200_OK, message="OTP has successfully validated.")

class ResetPasswordView(generics.GenericAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        tags=['Auth'],
        operation_description="This API allows users to reset their password. It requires the user to submit both a new password and a confirmation of the new password in the payload. Upon successful submission, the user's password is reset.",
        operation_summary="Reset Password API"
    )
    def post(self, request):
        """
        A function that is used to reset the password of a user.
        
        :param request: The request object
        """
        serializer = self.serializer_class(data=request.data,context={'request':request})
        
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return response(data={}, status_code=status.HTTP_200_OK, message="successful changing of the password.")


@method_decorator(name='get', decorator=swagger_auto_schema(
    tags=['Users'],
    operation_description="The Retrieve user profile API is an API that allows users to access their profile information.",
    operation_summary="Retrieve user profile API."
))
@method_decorator(name='put', decorator=swagger_auto_schema(auto_schema=None))
@method_decorator(name='patch', decorator=swagger_auto_schema(
    tags=['Users'],
    operation_description="The update profile API can be used to update a profile’s information in a given database.",
    operation_summary="Update user profile API.",
))
class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UpdateProfileSerializer
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        """
        It retrieves the profile of the user.
        
        :param request: The request object
        """
        instance = self.request.user
        serializer = self.get_serializer(instance)
        response_data = {**serializer.data,**{}}
        try:
            subscription = instance.get_active_plan()
            if subscription.exists():
                price = stripe.Price.retrieve(id=subscription[0].price_id)
                product = stripe.Product.retrieve(id=price['product'])
                response_data = {**response_data, **{'plan':{**price, **{'product':product}}}}
            else:
                response_data = {**response_data, **{'plan':{}}}
        except Exception:
            return response(data={}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, message="Oops! something went wrong!")
        return response(data=response_data, status_code=status.HTTP_200_OK, message="profile found successfully.")

    def patch(self, request, *args, **kwargs):
        """
        It updates the profile of the user.
        
        :param request: The request object
        """
        partial = kwargs.pop('partial', False)
        instance = self.request.user
        serializer = self.get_serializer(instance, data=request.data, partial=partial, context={"request": request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            if 'files' in request.FILES:
                instance.profile_image = request.FILES['files']
                instance.save()
            return response(data=serializer.data, status_code=status.HTTP_200_OK, message="profile updated successfully.")

class ChangePasswordView(generics.CreateAPIView):    
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=['Users'],
        operation_description= "This API takes the old and new passwords to change existing password.",
        operation_summary="Change Password API."
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return response(data={}, status_code=status.HTTP_200_OK, message="successful changing of the password.")
    

class ResendUserTokenView(generics.GenericAPIView):
    serializer_class = ResendUserTokenSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        tags=['Auth'],
        operation_description="This API allows users to reset their password. It requires the user to submit both a new password and a confirmation of the new password in the payload. Upon successful submission, the user's password is reset.",
        operation_summary="Reset Password API"
    )
    def post(self, request):
        """
        A function that is used to reset the password of a user.
        
        :param request: The request object
        """
        serializer = self.serializer_class(data=request.data,context={'request':request})
        
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return response(data={}, status_code=status.HTTP_200_OK, message="A new verification link has been sent to your mail")


class VerifyUserTokenView(viewsets.ViewSet):

    serializer_class = VerifyUserTokenSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        method = 'get',
        operation_description= "Verify User token",
        operation_summary="API to verify user token to complete signing process.",
        tags=['Auth']

    )
    @action(methods=['GET'], detail=True)
    def verify_token(self, request, token):
        serializer = self.serializer_class(data={'token':token},context={'request':request})
        
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return response(data={}, status_code=status.HTTP_200_OK, message="Your acount has been verified successfully")

@method_decorator(name='list', decorator=swagger_auto_schema(tags=['Users'], operation_description= "List API.", operation_summary="API to get list of records."))
@method_decorator(name='create', decorator=swagger_auto_schema(tags=['Users'], auto_schema=None))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(tags=['Users'], operation_description= "Retrieve API.", operation_summary="API for retrieve single record by id."))
@method_decorator(name='update', decorator=swagger_auto_schema(tags=['Users'], auto_schema=None))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(tags=['Users'], operation_description= "Partial update API.", operation_summary="API for partial update record."))
@method_decorator(name='destroy', decorator=swagger_auto_schema(tags=['Users'], operation_description= "Delete API.", operation_summary="API to delete single record by id."))
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(~Q(role_id=1))
    serializer_class = EndUserSerializer
    permission_classes = [CustomIsAdminUser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['email', 'first_name', 'last_name', 'updated_at', 'role__name', 'subscription__plan_type']
    filterset_fields = ['email', 'first_name', 'last_name']
    ordering_fields = ['email', 'first_name', 'first_name', 'updated_at', 'role__name', 'subscription__plan_type']

    def list(self, request, *args, **kwargs):
        self.serializer_class = UserResponseSerializer
        serializer = super().list(request, *args, **kwargs)
        return response(data=serializer.data, status_code=status.HTTP_200_OK, message="record found successfully")

    def retrieve(self, request, *args, **kwargs):
        self.serializer_class = UserResponseSerializer
        serializer = super().retrieve(request, *args, **kwargs)
        return response(data=serializer.data, status_code=status.HTTP_200_OK, message="record found successfully")
    
    def create(self, request, *args, **kwargs):
        self.serializer_class = UserResponseSerializer
        serializer = super().create(request, *args, **kwargs)
        return response(data=serializer.data, status_code=status.HTTP_200_OK, message="record successfully added in database.")
    
    def partial_update(self, request, *args, **kwargs):
        self.serializer_class = UserResponseSerializer
        serializer = super().partial_update(request, *args, **kwargs)
        return response(data=serializer.data, status_code=status.HTTP_200_OK, message="record successfully updated in database.")
    
    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return response(data={}, status_code=status.HTTP_200_OK, message="record deleted successfully")
    

@method_decorator(name='list', decorator=swagger_auto_schema(tags=['Roles'], operation_description= "List API.", operation_summary="API to get list of records."))
@method_decorator(name='create', decorator=swagger_auto_schema(tags=['Roles'], operation_description= "Create API.", operation_summary="API to create new record."))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(tags=['Roles'], operation_description= "Retrieve API.", operation_summary="API for retrieve single record by id."))
@method_decorator(name='update', decorator=swagger_auto_schema(tags=['Roles'], auto_schema=None))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(tags=['Roles'], operation_description= "Partial update API.", operation_summary="API for partial update record."))
@method_decorator(name='destroy', decorator=swagger_auto_schema(tags=['Roles'], operation_description= "Delete API.", operation_summary="API to delete single record by id."))
class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [CustomIsAdminUser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'tool_access', 'target_access', 'client_name_access', 'scan_result_access', 'cover_content_access', 'updated_at']
    filterset_fields = ['name']
    ordering_fields = ['name', 'tool_access', 'target_access', 'client_name_access', 'scan_result_access', 'cover_content_access', 'updated_at', 'is_verified']

    @swagger_auto_schema(
        method = 'get',
        operation_description= "Get all the roles without pagination",
        operation_summary="API to get all roles.",
        request_body=None,
        tags=['Roles']

    )
    @action(methods=['GET'], detail=False, url_path="all")
    def get_all(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return response(data=serializer.data, status_code=status.HTTP_200_OK, message="record found successfully")

    def list(self, request, *args, **kwargs):
        serializer = super().list(request, *args, **kwargs)
        return response(data=serializer.data, status_code=status.HTTP_200_OK, message="record found successfully")

    def retrieve(self, request, *args, **kwargs):
        serializer = super().retrieve(request, *args, **kwargs)
        return response(data=serializer.data, status_code=status.HTTP_200_OK, message="record found successfully")
    
    def create(self, request, *args, **kwargs):
        serializer = super().create(request, *args, **kwargs)
        return response(data=serializer.data, status_code=status.HTTP_200_OK, message="record successfully added in database.")
    
    def partial_update(self, request, *args, **kwargs):
        serializer = super().partial_update(request, *args, **kwargs)
        return response(data=serializer.data, status_code=status.HTTP_200_OK, message="record successfully updated in database.")
    
    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return response(data={}, status_code=status.HTTP_200_OK, message="record deleted successfully")
    