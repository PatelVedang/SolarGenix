from rest_framework.throttling import SimpleRateThrottle


class CustomAuthThrottle(SimpleRateThrottle):
    scope = "auth"

    def get_cache_key(self, request, view):
        if request.user.is_authenticated:
            ident = request.user.pk
        else:
            # Rate limit based on IP address
            ident = self.get_ident(request)
        ident = f"{ident}-{view.__class__.__name__}"
        return self.cache_format % {"scope": self.scope, "ident": ident}
