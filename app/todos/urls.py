from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TodoViewset

router = DefaultRouter(trailing_slash=True)
router.register(r"", TodoViewset)

urlpatterns = [
    path("todos/", include(router.urls)),
]
