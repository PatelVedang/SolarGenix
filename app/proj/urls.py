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

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf import settings
from django.conf.urls.static import static 

schema_view = get_schema_view(
   openapi.Info(
      title="Cyber Appliance API",
      default_version='1.0'
   ),
   public=True
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include([
        path('api/',include('user.urls')),
        path('api/',include('auth_api.urls')),
        # path('api/docs/', include('rest_framework.urls', namespace='rest_framework')),
        # path('api/docs/swagger-ui/', include('drf_yasg.urls')),  # Swagger UI
        path('swagger',schema_view.with_ui('swagger', cache_timeout=0), name='swagger-schema')
    ])),
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


admin.site.site_header = "ISAIX"
admin.site.site_title = "ISAIX Admin Portal"
admin.site.index_title = "Welcome to ISAIX Portal"
