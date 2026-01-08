from django.urls import path, include
from rest_framework.routers import DefaultRouter
from todos.views import TodoViewSet

router = DefaultRouter(trailing_slash=True)
router.register(r'', TodoViewSet)

urlpatterns = [
    path('todos/', include(router.urls)),
]
