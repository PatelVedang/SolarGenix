from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from utils.swagger import apply_swagger_tags
from utils.make_response import response

from .serializers import GoogleSocialAuthSerializer


# Create your views here.
@apply_swagger_tags(
    tags=["Google"],
    method_details={
        "post": {
            "operation_description": "Google API",
            "request_body": GoogleSocialAuthSerializer,
            "operation_summary": "Dynamic POST method to exchange token for Google",
        },
    },
)
class GoogleApi(APIView):
    def post(self, request):
        serializer = GoogleSocialAuthSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            message = data.get("message")
            data = data.get("data")
            return response(status_code=status.HTTP_200_OK, message=message, data=data)

        else:
            return Response(serializer.errors)
