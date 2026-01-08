from django.urls import path, include
from rest_framework.routers import DefaultRouter
from todos.views import TodosViewSet

router = DefaultRouter(trailing_slash=True)
router.register(r'', TodosViewSet)

urlpatterns = [
    path('todos/', include(router.urls)),
]
