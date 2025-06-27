import logging

from rest_framework.views import APIView
from utils.swagger import apply_swagger_tags

from auth_api.permissions import IsAuthenticated

# from utils.permissions import IsTokenValid
from auth_api.serializers import (
    CognitoSyncTokenSerializer,
    CreateCognitoRoleSerializer,
)
from auth_api.services import (
    CognitoSyncTokensViewService,
    CreateCognitoRoleAPIViewService,
)

logger = logging.getLogger("django")


@apply_swagger_tags(
    tags=["Auth"],
    method_details={
        "get": {
            "description": "Exchange Cognito code for tokens and sync user",
            "summary": "GET method for Cognito token sync using code",
        },
    },
)
class CognitoSyncTokensView(APIView):
    """
    APIView for synchronizing Cognito tokens.
    This view handles GET requests to synchronize tokens with AWS Cognito.
    It uses the `CognitoSyncTokenSerializer` for serialization and delegates
    the main logic to `CognitoSyncTokensViewService`.
    Methods:
        get(request): Handles GET requests and returns the response from the service layer.
    """
 
    serializer_class = CognitoSyncTokenSerializer

    def get(self, request):
        service = CognitoSyncTokensViewService()
        response_data = service.post_execute(request)
        return response_data


@apply_swagger_tags(
    tags=["Auth"],
    method_details={
        "post": {
            "description": "Create a new group in both Django and AWS Cognito",
            "summary": "POST method to create group in Django and sync with Cognito",
        }
    },
)
class CreateCognitoRoleAPIView(APIView):
    """
    API view for creating a Cognito role.
    This view handles POST requests to create a new Cognito role using the provided serializer.
    It requires the user to be authenticated.
    Methods:
        post(request):
            Handles the creation of a Cognito role by delegating to the CreateCognitoRoleAPIViewService.
            Returns the response data from the service.
    """
     
    permission_classes = [IsAuthenticated]
    serializer_class = CreateCognitoRoleSerializer

    def post(self, request):
        service = CreateCognitoRoleAPIViewService()
        response_data = service.post_execute(request)
        return response_data
