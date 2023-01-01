"""
Admin configuration for chat analysis app
"""
from django.contrib import admin
from .models import ChatAnalysis, ChatParticipant, ChatMessage, AnalysisReport


@admin.register(ChatAnalysis)
class ChatAnalysisAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'user', 'status', 'total_messages', 'total_participants',
        'overall_sentiment_label', 'created_at'
    )
    list_filter = ('status', 'detected_language', 'overall_sentiment_label', 'created_at')
    search_fields = ('title', 'user__email', 'original_filename')
    readonly_fields = ('file_hash', 'processing_duration', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('user', 'title', 'original_filename', 'file_size', 'file_hash')
        }),
        ('Processing', {
            'fields': ('status', 'processing_started_at', 'processing_completed_at', 
                      'processing_duration', 'error_message')
        }),
        ('Results', {
            'fields': ('detected_language', 'total_messages', 'total_participants',
                      'date_range_start', 'date_range_end', 'overall_sentiment_score',
                      'overall_sentiment_label', 'dominant_emotion', 'toxicity_score')
        }),
        ('Settings', {
            'fields': ('is_public', 'anonymize_participants')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(ChatParticipant)
class ChatParticipantAdmin(admin.ModelAdmin):
    list_display = (
        'anonymized_name', 'chat_analysis', 'message_count', 'word_count',
        'avg_sentiment_score', 'dominant_emotion'
    )
    list_filter = ('dominant_emotion', 'most_active_day')
    search_fields = ('anonymized_name', 'original_name', 'chat_analysis__title')


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = (
        'participant', 'message_type', 'timestamp', 'sentiment_label',
        'dominant_emotion', 'word_count'
    )
    list_filter = (
        'message_type', 'sentiment_label', 'dominant_emotion',
        'language_detected', 'contains_emoji', 'contains_url'
    )
    search_fields = ('original_text', 'participant__anonymized_name')
    readonly_fields = ('processed_at',)


@admin.register(AnalysisReport)
class AnalysisReportAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'chat_analysis', 'report_type', 'format',
        'file_size', 'download_count', 'generated_at'
    )
    list_filter = ('report_type', 'format', 'generated_at')
    search_fields = ('title', 'chat_analysis__title')
    readonly_fields = ('generated_at', 'generation_duration')