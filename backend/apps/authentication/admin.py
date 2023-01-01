"""
Admin configuration for authentication app
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, UserProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom User admin
    """
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'preferred_language', 'theme_preference')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {
            'fields': ('first_name', 'last_name', 'email', 'avatar', 'bio', 'location', 'birth_date')
        }),
        (_('Preferences'), {
            'fields': ('preferred_language', 'theme_preference', 'allow_data_collection', 'allow_analytics')
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Security'), {'fields': ('last_login_ip',)}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    User Profile admin
    """
    list_display = (
        'user', 'subscription_type', 'total_chats_analyzed', 
        'api_calls_count', 'api_calls_remaining', 'created_at'
    )
    list_filter = ('subscription_type', 'created_at')
    search_fields = ('user__email', 'user__username', 'user__first_name', 'user__last_name')
    readonly_fields = ('created_at', 'updated_at', 'api_calls_reset_date')
    
    fieldsets = (
        (_('User'), {'fields': ('user',)}),
        (_('Usage Statistics'), {
            'fields': ('total_chats_analyzed', 'total_messages_processed', 'favorite_analysis_type')
        }),
        (_('Subscription'), {
            'fields': ('subscription_type', 'subscription_expires')
        }),
        (_('API Usage'), {
            'fields': ('api_calls_count', 'api_calls_limit', 'api_calls_reset_date')
        }),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at')}),
    )
    
    def api_calls_remaining(self, obj):
        return obj.api_calls_remaining
    api_calls_remaining.short_description = 'API Calls Remaining'