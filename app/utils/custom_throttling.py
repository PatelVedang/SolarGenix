from rest_framework.throttling import SimpleRateThrottle


class CustomAuthThrottle(SimpleRateThrottle):

    scope = "auth"

    def get_cache_key(self, request, view):
        """
        Generates a unique cache key for throttling purposes based on the authenticated user or the client's IP address.

        If the user is authenticated, their primary key is used as the identifier; otherwise, the client's IP address is used.
        The identifier is further combined with the view's class name to ensure uniqueness per view.
        The final cache key is formatted using the defined cache format and scope.

        Args:
            request (HttpRequest): The incoming HTTP request object.
            view (APIView): The view instance handling the request.

        Returns:
            str: A formatted cache key string for throttling.
        """
        if request.user.is_authenticated:
            ident = request.user.pk
        else:
            # Rate limit based on IP address
            ident = self.get_ident(request)
        ident = f"{ident}-{view.__class__.__name__}"
        return self.cache_format % {"scope": self.scope, "ident": ident}
