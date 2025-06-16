from auth_api.serializers import UserRegistrationSerializer


class UserRegisterViewService:
    def post_execute(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response_data = serializer.data
        return response_data
