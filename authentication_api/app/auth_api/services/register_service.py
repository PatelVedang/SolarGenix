from auth_api.serializers import UserRegistrationSerializer


class UserRegisterViewService:
    """
    Service class for handling user registration logic.

    Methods
    -------
    post_execute(request):
        Handles the user registration process. Validates the incoming request data using
        UserRegistrationSerializer, saves the new user if data is valid, and returns the
        serialized user data as a response.
    """
    def post_execute(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response_data = serializer.data
        return response_data
