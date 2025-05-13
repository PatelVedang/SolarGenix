from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users.views import UserViewSet ,ExportUserView

router = DefaultRouter()
router.register(r"", UserViewSet)

urlpatterns = [
    path("users/", include(router.urls)),
    path("export-users/" ,ExportUserView.as_view() ,name="export-user")
]
