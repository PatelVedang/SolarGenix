from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DemoViewset

router = DefaultRouter(trailing_slash=True)
router.register(r"", DemoViewset)

urlpatterns = [
    path("demos/", include(router.urls)),
]
