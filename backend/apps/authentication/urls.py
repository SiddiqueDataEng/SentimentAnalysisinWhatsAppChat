"""
URL configuration for authentication app
"""
from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    # Authentication endpoints
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Profile management
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    path('stats/', views.UserStatsView.as_view(), name='user_stats'),
    
    # Account management
    path('delete-account/', views.delete_account_view, name='delete_account'),
    
    # Health check
    path('health/', views.auth_health_check, name='auth_health'),
]