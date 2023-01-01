"""
URLs for analytics app
"""
from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('overview/', views.user_analytics_overview, name='user_overview'),
    path('sentiment-trends/<uuid:analysis_id>/', views.sentiment_trends, name='sentiment_trends'),
]