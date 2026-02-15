from django.urls import path

from .views.bill_prediction_view import BillPredictionView
from .views.chatbot_view import (
    ChatbotAPIView,
    DeleteKnowledgeBaseAPIView,
    PDFIngestionAPIView,
)
from .views.solar_gen_prediction_view import SolarGenerationPrediction

urlpatterns = [
    path('predict-production/', SolarGenerationPrediction.as_view(), name='solar-generation-predict'),
    path('predict-bill/', BillPredictionView.as_view(), name='bill-prediction'),
    path('chatbot/ask/', ChatbotAPIView.as_view(), name='chatbot-ask'),
    path('chatbot/ingest-pdf/', PDFIngestionAPIView.as_view(), name='chatbot-ingest-pdf'),
    path('chatbot/delete-knowledge-base/', DeleteKnowledgeBaseAPIView.as_view(), name='chatbot-delete-knowledge-base'),
]