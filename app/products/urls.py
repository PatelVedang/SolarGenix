from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewset

router = DefaultRouter(trailing_slash=True)
router.register(r"", ProductViewset)

urlpatterns = [
    path("products/", include(router.urls)),
]
