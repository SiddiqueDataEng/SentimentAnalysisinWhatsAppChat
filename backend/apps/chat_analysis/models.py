"""
Models for WhatsApp chat analysis
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
import uuid
import json

User = get_user_model()


class ChatAnalysis(models.Model):
    """
    Main model for storing chat analysis results
    """
    ANALYSIS_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('hi', 'Hindi'),
        ('hinglish', 'Hinglish'),
        ('mixed', 'Mixed'),
        ('unknown', 'Unknown'),
    ]
    
    # Basic info
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_analyses')
    title = models.CharField(max_length=200, help_text="Chat title or description")
    
    # File info
    original_filename = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField(help_text="File size in bytes")
    file_hash = models.CharField(max_length=64, help_text="SHA256 hash of the file")
    
    # Analysis metadata
    status = models.CharField(max_length=20, choices=ANALYSIS_STATUS_CHOICES, default='pending')
    detected_language = models.CharField(max_length=20, choices=LANGUAGE_CHOICES, default='unknown')
    total_messages = models.PositiveIntegerField(default=0)
    total_participants = models.PositiveIntegerField(default=0)
    date_range_start = models.DateTimeField(null=True, blank=True)
    date_range_end = models.DateTimeField(null=True, blank=True)
    
    # Processing info
    processing_started_at = models.DateTimeField(null=True, blank=True)
    processing_completed_at = models.DateTimeField(null=True, blank=True)
    processing_duration = models.DurationField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    # Results summary
    overall_sentiment_score = models.FloatField(null=True, blank=True, help_text="Overall sentiment score (-1 to 1)")
    overall_sentiment_label = models.CharField(max_length=20, blank=True)
    dominant_emotion = models.CharField(max_length=20, blank=True)
    toxicity_score = models.FloatField(null=True, blank=True, help_text="Toxicity score (0 to 1)")
    
    # Privacy settings
    is_public = models.BooleanField(default=False)
    anonymize_participants = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'chat_analyses'
        verbose_name = _('Chat Analysis')
        verbose_name_plural = _('Chat Analyses')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['detected_language']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.user.email}"
    
    @property
    def is_completed(self):
        return self.status == 'completed'
    
    @property
    def is_processing(self):
        return self.status in ['pending', 'processing']
    
    @property
    def success_rate(self):
        if self.total_messages == 0:
            return 0
        processed_messages = self.messages.filter(sentiment_score__isnull=False).count()
        return (processed_messages / self.total_messages) * 100


class ChatParticipant(models.Model):
    """
    Model for chat participants
    """
    chat_analysis = models.ForeignKey(ChatAnalysis, on_delete=models.CASCADE, related_name='participants')
    
    # Participant info
    original_name = models.CharField(max_length=255, help_text="Original name from chat")
    anonymized_name = models.CharField(max_length=50, help_text="Anonymized name for display")
    participant_id = models.CharField(max_length=50, help_text="Unique identifier within chat")
    
    # Statistics
    message_count = models.PositiveIntegerField(default=0)
    word_count = models.PositiveIntegerField(default=0)
    avg_sentiment_score = models.FloatField(null=True, blank=True)
    dominant_emotion = models.CharField(max_length=20, blank=True)
    
    # Activity patterns
    most_active_hour = models.PositiveSmallIntegerField(null=True, blank=True)
    most_active_day = models.CharField(max_length=10, blank=True)
    first_message_date = models.DateTimeField(null=True, blank=True)
    last_message_date = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'chat_participants'
        verbose_name = _('Chat Participant')
        verbose_name_plural = _('Chat Participants')
        unique_together = ['chat_analysis', 'participant_id']
        indexes = [
            models.Index(fields=['chat_analysis', 'message_count']),
        ]
    
    def __str__(self):
        return f"{self.anonymized_name} in {self.chat_analysis.title}"


class ChatMessage(models.Model):
    """
    Model for individual chat messages
    """
    MESSAGE_TYPE_CHOICES = [
        ('text', 'Text'),
        ('media', 'Media'),
        ('system', 'System'),
        ('deleted', 'Deleted'),
    ]
    
    chat_analysis = models.ForeignKey(ChatAnalysis, on_delete=models.CASCADE, related_name='messages')
    participant = models.ForeignKey(ChatParticipant, on_delete=models.CASCADE, related_name='messages')
    
    # Message content
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPE_CHOICES, default='text')
    original_text = models.TextField(help_text="Original message text")
    cleaned_text = models.TextField(help_text="Cleaned text for analysis")
    word_count = models.PositiveIntegerField(default=0)
    
    # Timestamp info
    timestamp = models.DateTimeField(help_text="Message timestamp from chat")
    hour = models.PositiveSmallIntegerField()
    day_of_week = models.PositiveSmallIntegerField()
    
    # Sentiment analysis results
    sentiment_score = models.FloatField(null=True, blank=True, help_text="Sentiment score (-1 to 1)")
    sentiment_label = models.CharField(max_length=20, blank=True)
    sentiment_confidence = models.FloatField(null=True, blank=True)
    
    # Emotion analysis
    emotion_scores = models.JSONField(default=dict, help_text="Emotion scores as JSON")
    dominant_emotion = models.CharField(max_length=20, blank=True)
    emotion_confidence = models.FloatField(null=True, blank=True)
    
    # Additional analysis
    toxicity_score = models.FloatField(null=True, blank=True)
    language_detected = models.CharField(max_length=10, blank=True)
    contains_emoji = models.BooleanField(default=False)
    emoji_count = models.PositiveIntegerField(default=0)
    contains_url = models.BooleanField(default=False)
    url_count = models.PositiveIntegerField(default=0)
    
    # Processing info
    processed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'chat_messages'
        verbose_name = _('Chat Message')
        verbose_name_plural = _('Chat Messages')
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['chat_analysis', 'timestamp']),
            models.Index(fields=['participant', 'timestamp']),
            models.Index(fields=['sentiment_score']),
            models.Index(fields=['dominant_emotion']),
        ]
    
    def __str__(self):
        return f"Message by {self.participant.anonymized_name} at {self.timestamp}"
    
    @property
    def is_positive(self):
        return self.sentiment_score and self.sentiment_score > 0.1
    
    @property
    def is_negative(self):
        return self.sentiment_score and self.sentiment_score < -0.1
    
    @property
    def is_neutral(self):
        return self.sentiment_score and -0.1 <= self.sentiment_score <= 0.1


class AnalysisReport(models.Model):
    """
    Model for generated analysis reports
    """
    REPORT_TYPE_CHOICES = [
        ('summary', 'Summary Report'),
        ('detailed', 'Detailed Report'),
        ('comparison', 'Comparison Report'),
        ('custom', 'Custom Report'),
    ]
    
    FORMAT_CHOICES = [
        ('json', 'JSON'),
        ('pdf', 'PDF'),
        ('csv', 'CSV'),
        ('html', 'HTML'),
    ]
    
    chat_analysis = models.ForeignKey(ChatAnalysis, on_delete=models.CASCADE, related_name='reports')
    
    # Report info
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES)
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Report data
    report_data = models.JSONField(help_text="Report data as JSON")
    file_path = models.CharField(max_length=500, blank=True, help_text="Path to generated file")
    file_size = models.PositiveIntegerField(null=True, blank=True)
    
    # Generation info
    generated_at = models.DateTimeField(auto_now_add=True)
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    generation_duration = models.DurationField(null=True, blank=True)
    
    # Access info
    download_count = models.PositiveIntegerField(default=0)
    last_downloaded_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'analysis_reports'
        verbose_name = _('Analysis Report')
        verbose_name_plural = _('Analysis Reports')
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"{self.title} ({self.format.upper()})"