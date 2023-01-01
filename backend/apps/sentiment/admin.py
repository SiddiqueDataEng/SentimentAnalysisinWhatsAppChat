"""
Sentiment analysis admin configuration
"""
from django.contrib import admin
from .models import SentimentModel, ModelPerformance


@admin.register(SentimentModel)
class SentimentModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'version', 'model_type', 'is_active', 'accuracy_score')
    list_filter = ('model_type', 'is_active')
    search_fields = ('name', 'version')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ModelPerformance)
class ModelPerformanceAdmin(admin.ModelAdmin):
    list_display = ('model', 'accuracy', 'precision', 'recall', 'f1_score', 'test_date')
    list_filter = ('test_date', 'model')
    readonly_fields = ('test_date',)
    date_hierarchy = 'test_date'