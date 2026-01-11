from django.contrib import admin
from django.urls import path
from django.urls import include
from .views.solar_gen_prediction_view import SolarGenerationPrediction
from .views.bill_prediction_view import BillPredictionView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('predict-production/', SolarGenerationPrediction.as_view(), name='solar-generation-predict'),
    path('predict-bill/', BillPredictionView.as_view(), name='bill-prediction'),
]