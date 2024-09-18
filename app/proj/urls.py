"""proj URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_yasg import openapi
from drf_yasg.views import get_schema_view

schema_view = get_schema_view(
    openapi.Info(title="Boilerplate API", default_version="1.0"), public=True
)

# urlpatterns = [
#     path("admin/", admin.site.urls),
#     path(
#         "",
#         include(
#             [
#                 path("api/", include("auth_api.urls")),
#                 path(
#                     "swagger",
#                     schema_view.with_ui("swagger", cache_timeout=0),
#                     name="swagger-schema",
#                 ),
#                 path("api/", include("google_sso.urls")),
#             ]
#         ),
#     ),
# ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "",
        include(
            [
                # IMPORT_NEW_ROUTE_HERE
                path("api/", include("demos.urls")),
                path("api/", include("auth_api.urls")),
                path("api/", include("users.urls")),
                path("api/", include("todos.urls")),
                path(
                    "swagger",
                    schema_view.with_ui("swagger", cache_timeout=0),
                    name="swagger-schema",
                ),
            ]
        ),
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = "ADMINISTRATION"
admin.site.site_title = "Admin Portal"
admin.site.index_title = "Welcome to Admin Portal"
