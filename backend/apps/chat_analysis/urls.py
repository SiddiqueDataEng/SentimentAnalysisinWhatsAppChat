"""
URLs for chat analysis app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'chat_analysis'

router = DefaultRouter()
router.register(r'analyses', views.ChatAnalysisViewSet, basename='chatanalysis')

urlpatterns = [
    path('', include(router.urls)),
]