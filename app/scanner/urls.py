from django.urls import path, include
from . import views
from .views import ScanViewSet, ToolViewSet
from rest_framework import routers
from drf_yasg.utils import swagger_auto_schema

# decorated_login_view = swagger_auto_schema(method='get')(ToolViewSet.as_view())

router = routers.DefaultRouter()
router.register('targets', ScanViewSet,basename='targets')
router.register('tool', ToolViewSet,basename='tool')

urlpatterns = [
    path('', include(router.urls)),
    path('sendMessage/', views.SendMessageView.as_view(), name='Message'),
]
