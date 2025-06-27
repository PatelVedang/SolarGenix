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
    This view is called by Cognito after user login via the hosted UI.
    It receives the `code` as a query param, exchanges it for tokens,
    manages the user and tokens, and returns the relevant data.
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
    permission_classes = [IsAuthenticated]
    serializer_class = CreateCognitoRoleSerializer

    def post(self, request):
        service = CreateCognitoRoleAPIViewService()
        response_data = service.post_execute(request)
        return response_data
