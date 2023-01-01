"""
Analytics admin configuration
"""
from django.contrib import admin
from .models import AnalyticsEvent, SystemMetrics


@admin.register(AnalyticsEvent)
class AnalyticsEventAdmin(admin.ModelAdmin):
    list_display = ('user', 'event_type', 'timestamp', 'ip_address')
    list_filter = ('event_type', 'timestamp')
    search_fields = ('user__email', 'event_type')
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'


@admin.register(SystemMetrics)
class SystemMetricsAdmin(admin.ModelAdmin):
    list_display = ('metric_name', 'metric_value', 'metric_unit', 'timestamp')
    list_filter = ('metric_name', 'timestamp')
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'