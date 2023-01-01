"""
Core app URLs
"""
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.health_check, name='health_check'),
    path('info/', views.system_info, name='system_info'),
]