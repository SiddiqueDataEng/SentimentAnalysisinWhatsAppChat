"""
Serializers for chat analysis app
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import ChatAnalysis, ChatParticipant, ChatMessage, AnalysisReport
import hashlib

User = get_user_model()


class ChatAnalysisCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new chat analysis
    """
    file = serializers.FileField(write_only=True)
    
    class Meta:
        model = ChatAnalysis
        fields = (
            'title', 'file', 'anonymize_participants', 'is_public'
        )
    
    def validate_file(self, value):
        """Validate uploaded file"""
        # Check file size (max 50MB)
        if value.size > 50 * 1024 * 1024:
            raise serializers.ValidationError("File size cannot exceed 50MB")
        
        # Check file extension
        allowed_extensions = ['.txt']
        file_extension = value.name.lower().split('.')[-1]
        if f'.{file_extension}' not in allowed_extensions:
            raise serializers.ValidationError("Only .txt files are allowed")
        
        return value
    
    def create(self, validated_data):
        file = validated_data.pop('file')
        user = self.context['request'].user
        
        # Read file content
        file_content = file.read().decode('utf-8')
        
        # Calculate file hash
        file_hash = hashlib.sha256(file_content.encode('utf-8')).hexdigest()
        
        # Check for duplicate
        existing_analysis = ChatAnalysis.objects.filter(
            user=user,
            file_hash=file_hash
        ).first()
        
        if existing_analysis:
            raise serializers.ValidationError(
                "This chat file has already been analyzed. "
                f"Analysis ID: {existing_analysis.id}"
            )
        
        # Create chat analysis
        chat_analysis = ChatAnalysis.objects.create(
            user=user,
            original_filename=file.name,
            file_size=file.size,
            file_hash=file_hash,
            **validated_data
        )
        
        # Start processing task
        from .tasks import process_whatsapp_chat
        process_whatsapp_chat.delay(str(chat_analysis.id), file_content)
        
        return chat_analysis


class ChatParticipantSerializer(serializers.ModelSerializer):
    """
    Serializer for chat participants
    """
    class Meta:
        model = ChatParticipant
        fields = (
            'anonymized_name', 'message_count', 'word_count',
            'avg_sentiment_score', 'dominant_emotion',
            'most_active_hour', 'most_active_day',
            'first_message_date', 'last_message_date'
        )


class ChatMessageSerializer(serializers.ModelSerializer):
    """
    Serializer for chat messages
    """
    participant_name = serializers.CharField(source='participant.anonymized_name', read_only=True)
    
    class Meta:
        model = ChatMessage
        fields = (
            'id', 'participant_name', 'message_type', 'original_text',
            'word_count', 'timestamp', 'hour', 'day_of_week',
            'sentiment_score', 'sentiment_label', 'sentiment_confidence',
            'emotion_scores', 'dominant_emotion', 'emotion_confidence',
            'toxicity_score', 'language_detected', 'contains_emoji',
            'emoji_count', 'contains_url', 'url_count'
        )


class ChatAnalysisListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing chat analyses
    """
    processing_duration_seconds = serializers.SerializerMethodField()
    success_rate = serializers.ReadOnlyField()
    
    class Meta:
        model = ChatAnalysis
        fields = (
            'id', 'title', 'status', 'detected_language',
            'total_messages', 'total_participants',
            'overall_sentiment_score', 'overall_sentiment_label',
            'dominant_emotion', 'toxicity_score',
            'date_range_start', 'date_range_end',
            'processing_duration_seconds', 'success_rate',
            'created_at', 'updated_at'
        )
    
    def get_processing_duration_seconds(self, obj):
        if obj.processing_duration:
            return obj.processing_duration.total_seconds()
        return None


class ChatAnalysisDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for chat analysis
    """
    participants = ChatParticipantSerializer(many=True, read_only=True)
    processing_duration_seconds = serializers.SerializerMethodField()
    success_rate = serializers.ReadOnlyField()
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = ChatAnalysis
        fields = (
            'id', 'title', 'user_email', 'original_filename',
            'file_size', 'status', 'detected_language',
            'total_messages', 'total_participants',
            'date_range_start', 'date_range_end',
            'overall_sentiment_score', 'overall_sentiment_label',
            'dominant_emotion', 'toxicity_score',
            'processing_started_at', 'processing_completed_at',
            'processing_duration_seconds', 'success_rate',
            'error_message', 'is_public', 'anonymize_participants',
            'participants', 'created_at', 'updated_at'
        )
    
    def get_processing_duration_seconds(self, obj):
        if obj.processing_duration:
            return obj.processing_duration.total_seconds()
        return None


class AnalysisReportSerializer(serializers.ModelSerializer):
    """
    Serializer for analysis reports
    """
    file_size_mb = serializers.SerializerMethodField()
    generation_duration_seconds = serializers.SerializerMethodField()
    
    class Meta:
        model = AnalysisReport
        fields = (
            'id', 'report_type', 'format', 'title', 'description',
            'file_size_mb', 'generation_duration_seconds',
            'download_count', 'generated_at', 'last_downloaded_at'
        )
    
    def get_file_size_mb(self, obj):
        if obj.file_size:
            return round(obj.file_size / (1024 * 1024), 2)
        return None
    
    def get_generation_duration_seconds(self, obj):
        if obj.generation_duration:
            return obj.generation_duration.total_seconds()
        return None


class ChatAnalysisStatsSerializer(serializers.Serializer):
    """
    Serializer for chat analysis statistics
    """
    total_analyses = serializers.IntegerField()
    completed_analyses = serializers.IntegerField()
    processing_analyses = serializers.IntegerField()
    failed_analyses = serializers.IntegerField()
    total_messages_processed = serializers.IntegerField()
    avg_processing_time = serializers.FloatField()
    most_common_language = serializers.CharField()
    sentiment_distribution = serializers.DictField()
    emotion_distribution = serializers.DictField()


class MessageFilterSerializer(serializers.Serializer):
    """
    Serializer for message filtering parameters
    """
    participant = serializers.CharField(required=False)
    sentiment_label = serializers.ChoiceField(
        choices=['positive', 'negative', 'neutral'],
        required=False
    )
    emotion = serializers.CharField(required=False)
    date_from = serializers.DateTimeField(required=False)
    date_to = serializers.DateTimeField(required=False)
    min_sentiment_score = serializers.FloatField(required=False)
    max_sentiment_score = serializers.FloatField(required=False)
    contains_emoji = serializers.BooleanField(required=False)
    contains_url = serializers.BooleanField(required=False)
    message_type = serializers.ChoiceField(
        choices=['text', 'media', 'system'],
        required=False
    )
    search_text = serializers.CharField(required=False)
    
    def validate(self, data):
        """Validate filter parameters"""
        if 'date_from' in data and 'date_to' in data:
            if data['date_from'] > data['date_to']:
                raise serializers.ValidationError(
                    "date_from must be before date_to"
                )
        
        if 'min_sentiment_score' in data and 'max_sentiment_score' in data:
            if data['min_sentiment_score'] > data['max_sentiment_score']:
                raise serializers.ValidationError(
                    "min_sentiment_score must be less than max_sentiment_score"
                )
        
        return data