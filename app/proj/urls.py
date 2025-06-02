# """proj URL Configuration

# The `urlpatterns` list routes URLs to views. For more information please see:
#     https://docs.djangoproject.com/en/4.1/topics/http/urls/
# Examples:
# Function views
#     1. Add an import:  from my_app import views
#     2. Add a URL to urlpatterns:  path('', views.home, name='home')
# Class-based views
#     1. Add an import:  from other_app.views import Home
#     2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
# Including another URLconf
#     1. Import the include() function: from django.urls import include, path
#     2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
# """

from django.conf import settings
from django.conf.urls import handler404, handler500
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)
from utils.swagger import swagger_auth_required

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "api/",
        include(
            [
                # IMPORT_NEW_ROUTE_HERE
                # path("", include("auth_api.urls")),
                path("", include("auth_api.urls")),
                path("", include("users.urls")),
                path("", include("todos.urls")),
            ]
        ),
    ),
    path(
        "api/schema/",
        SpectacularAPIView.as_view(),
        name="schema",
    ),
    path(
        "swagger/",
        swagger_auth_required(SpectacularSwaggerView.as_view(url_name="schema")),
        name="swagger-ui",
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


'''The lines `handler404 = 'proj.base_view.handler404'` and `handler500 = 'proj.base_view.handler500'`
in the Django URL configuration are setting custom error handlers for handling HTTP 404 (Page Not
Found) and HTTP 500 (Server Error) responses.'''
handler404 = "proj.base_view.handler404"  # noqa
handler500 = "proj.base_view.handler500"  # noqa

admin.site.site_header = "ADMINISTRATION"
admin.site.site_title = settings.PROJECT_TITLE
admin.site.index_title = f"Welcome to Admin Portal of {settings.PROJECT_TITLE}"
