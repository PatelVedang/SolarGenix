from django.urls import path

from .views.bill_prediction_view import BillPredictionView
from .views.chatbot_view import (
    ChatbotAPIView,
    CrawlerAPIView,
    PDFIngestionAPIView,
)
from .views.solar_gen_prediction_view import SolarGenerationPrediction

urlpatterns = [
    path('predict-production/', SolarGenerationPrediction.as_view(), name='solar-generation-predict'),
    path('predict-bill/', BillPredictionView.as_view(), name='bill-prediction'),
    path('chatbot/ask/', ChatbotAPIView.as_view(), name='chatbot-ask'),
    path('chatbot/crawl/', CrawlerAPIView.as_view(), name='chatbot-crawl'),
    path('chatbot/ingest-pdf/', PDFIngestionAPIView.as_view(), name='chatbot-ingest-pdf'),
]