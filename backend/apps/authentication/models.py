"""
Custom User model for WhatsApp Sentiment Analysis
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Custom User model with additional fields
    """
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=150)
    last_name = models.CharField(_('last name'), max_length=150)
    
    # Profile fields
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    
    # Preferences
    preferred_language = models.CharField(
        max_length=10,
        choices=[
            ('en', 'English'),
            ('hi', 'Hindi'),
            ('hinglish', 'Hinglish'),
        ],
        default='en'
    )
    theme_preference = models.CharField(
        max_length=10,
        choices=[
            ('light', 'Light'),
            ('dark', 'Dark'),
            ('auto', 'Auto'),
        ],
        default='auto'
    )
    
    # Privacy settings
    allow_data_collection = models.BooleanField(default=True)
    allow_analytics = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        db_table = 'auth_user'
        verbose_name = _('User')
        verbose_name_plural = _('Users')
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_short_name(self):
        return self.first_name


class UserProfile(models.Model):
    """
    Extended user profile information
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Usage statistics
    total_chats_analyzed = models.PositiveIntegerField(default=0)
    total_messages_processed = models.PositiveIntegerField(default=0)
    favorite_analysis_type = models.CharField(max_length=50, blank=True)
    
    # Subscription info
    subscription_type = models.CharField(
        max_length=20,
        choices=[
            ('free', 'Free'),
            ('premium', 'Premium'),
            ('enterprise', 'Enterprise'),
        ],
        default='free'
    )
    subscription_expires = models.DateTimeField(null=True, blank=True)
    
    # API usage
    api_calls_count = models.PositiveIntegerField(default=0)
    api_calls_limit = models.PositiveIntegerField(default=1000)
    api_calls_reset_date = models.DateTimeField(auto_now_add=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profiles'
        verbose_name = _('User Profile')
        verbose_name_plural = _('User Profiles')
    
    def __str__(self):
        return f"Profile of {self.user.full_name}"
    
    @property
    def is_premium(self):
        return self.subscription_type in ['premium', 'enterprise']
    
    @property
    def api_calls_remaining(self):
        return max(0, self.api_calls_limit - self.api_calls_count)