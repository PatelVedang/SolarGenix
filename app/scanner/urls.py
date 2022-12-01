from django.urls import path
from . import views
urlpatterns = [
    path('scan/', views.scanHost, name='scan'),
    
]
