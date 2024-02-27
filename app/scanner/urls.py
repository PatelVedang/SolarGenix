from django.urls import path, include
# from . import views
from . import views_v2 as views
from .views_v2 import ScanViewSet, ToolViewSet, OrderViewSet, SubscriptionViewSet
from rest_framework import routers
from drf_yasg.utils import swagger_auto_schema

# decorated_login_view = swagger_auto_schema(method='get')(ToolViewSet.as_view())

router = routers.DefaultRouter()
router.register('targets', ScanViewSet,basename='targets')
router.register('tool', ToolViewSet,basename='tool')
router.register('orders', OrderViewSet,basename='order')
router.register('subscriptions', SubscriptionViewSet,basename='subscriptions')

urlpatterns = [
    path('', include(router.urls)),
    path('sendMessage/', views.SendMessageView.as_view(), name='Message'),
    path('octopii/', views.OctopiiView.as_view(), name='octopii'),
]
