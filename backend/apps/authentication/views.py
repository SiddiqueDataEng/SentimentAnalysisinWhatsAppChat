"""
Authentication views for WhatsApp Sentiment Analysis
"""
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login, logout
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
import logging

from .models import User, UserProfile
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    UserProfileUpdateSerializer,
    ChangePasswordSerializer,
    UserStatsSerializer
)

logger = logging.getLogger(__name__)


class RegisterView(generics.CreateAPIView):
    """
    User registration endpoint
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        logger.info(f"New user registered: {user.email}")
        
        return Response({
            'user': UserProfileSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': 'Registration successful'
        }, status=status.HTTP_201_CREATED)


@method_decorator(csrf_exempt, name='dispatch')
class LoginView(generics.GenericAPIView):
    """
    User login endpoint
    """
    serializer_class = UserLoginSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        login(request, user)
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        # Update last login IP
        user.last_login_ip = self.get_client_ip(request)
        user.save(update_fields=['last_login_ip'])
        
        logger.info(f"User logged in: {user.email}")
        
        return Response({
            'user': UserProfileSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': 'Login successful'
        }, status=status.HTTP_200_OK)
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """
    User logout endpoint
    """
    try:
        refresh_token = request.data.get('refresh_token')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        
        logout(request)
        logger.info(f"User logged out: {request.user.email}")
        
        return Response({
            'message': 'Logout successful'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return Response({
            'error': 'Logout failed'
        }, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(generics.RetrieveUpdateAPIView):
    """
    User profile view and update
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def get_serializer_class(self):
        if self.request.method == 'PUT' or self.request.method == 'PATCH':
            return UserProfileUpdateSerializer
        return UserProfileSerializer
    
    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        logger.info(f"Profile updated: {request.user.email}")
        return response


class ChangePasswordView(generics.UpdateAPIView):
    """
    Change password endpoint
    """
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = self.get_object()
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        logger.info(f"Password changed: {user.email}")
        
        return Response({
            'message': 'Password changed successfully'
        }, status=status.HTTP_200_OK)


class UserStatsView(generics.RetrieveAPIView):
    """
    User statistics endpoint
    """
    serializer_class = UserStatsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_account_view(request):
    """
    Delete user account endpoint
    """
    user = request.user
    email = user.email
    
    # Soft delete - deactivate account
    user.is_active = False
    user.save()
    
    logger.warning(f"Account deactivated: {email}")
    
    return Response({
        'message': 'Account deactivated successfully'
    }, status=status.HTTP_200_OK)


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """
    Signal handler for user login
    """
    logger.info(f"User login signal: {user.email} from {request.META.get('REMOTE_ADDR')}")


# Health check for authentication service
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def auth_health_check(request):
    """
    Health check endpoint for authentication service
    """
    return Response({
        'status': 'healthy',
        'service': 'authentication',
        'timestamp': request.META.get('HTTP_DATE')
    }, status=status.HTTP_200_OK)