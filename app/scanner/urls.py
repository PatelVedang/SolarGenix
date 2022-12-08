from django.urls import path, include
from . import views
from .views import ScanViewSet
from rest_framework import routers

router = routers.DefaultRouter()
router.register('scan', ScanViewSet,basename='scan')

urlpatterns = [
    path('', include(router.urls)),
]
