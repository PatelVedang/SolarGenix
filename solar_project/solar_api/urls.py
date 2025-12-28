from django.contrib import admin
from django.urls import path
from django.urls import include
from .views import SolarGenerationPrediction

urlpatterns = [
    path('admin/', admin.site.urls),
    path('predict/', SolarGenerationPrediction.as_view(), name='solar-generation-predict'),
]