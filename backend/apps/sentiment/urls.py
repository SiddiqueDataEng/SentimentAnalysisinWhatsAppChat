"""
URLs for sentiment analysis app
"""
from django.urls import path
from . import views

app_name = 'sentiment'

urlpatterns = [
    path('models/', views.model_info, name='model_info'),
    path('analyze/', views.analyze_text, name='analyze_text'),
]