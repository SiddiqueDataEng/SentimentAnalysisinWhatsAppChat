"""
Analytics models
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class AnalyticsEvent(models.Model):
    """
    Model to track user analytics events
    """
    EVENT_TYPES = [
        ('chat_upload', 'Chat Upload'),
        ('analysis_complete', 'Analysis Complete'),
        ('report_download', 'Report Download'),
        ('api_call', 'API Call'),
        ('login', 'User Login'),
        ('logout', 'User Logout'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='analytics_events')
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    event_data = models.JSONField(default=dict)
    
    # Request metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    referer = models.URLField(blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'analytics_events'
        verbose_name = _('Analytics Event')
        verbose_name_plural = _('Analytics Events')
        indexes = [
            models.Index(fields=['user', 'event_type', 'timestamp']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.event_type} at {self.timestamp}"


class SystemMetrics(models.Model):
    """
    Model to store system-wide metrics
    """
    metric_name = models.CharField(max_length=100)
    metric_value = models.FloatField()
    metric_unit = models.CharField(max_length=50, blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'system_metrics'
        verbose_name = _('System Metric')
        verbose_name_plural = _('System Metrics')
        indexes = [
            models.Index(fields=['metric_name', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.metric_name}: {self.metric_value} {self.metric_unit}"