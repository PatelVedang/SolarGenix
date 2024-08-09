from django.urls import path

from .views import ExchangeTokenView, GoogleApi

urlpatterns = [
    path("google/", GoogleApi.as_view(), name="google"),
    path("exchange-token/", ExchangeTokenView.as_view(), name="exchange-token"),
]
