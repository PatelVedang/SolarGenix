from django.urls import path

from .views import GoogleApi

urlpatterns = [
    path("google/", GoogleApi.as_view(), name="google"),
]
