"""
Enhanced WhatsApp Chat Analysis Views
Production-ready with comprehensive error handling
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Avg
from django.utils import timezone
import logging
import json

from .models import ChatAnalysis, ChatParticipant, ChatMessage
from .serializers import (
    ChatAnalysisCreateSerializer,
    ChatAnalysisListSerializer,
    ChatAnalysisDetailSerializer,
    ChatMessageSerializer,
    ChatParticipantSerializer,
    MessageFilterSerializer
)
from .preprocessing import WhatsAppChatPreprocessor
from apps.sentiment.analyzers import MultiModelSentimentAnalyzer

logger = logging.getLogger(__name__)


class ChatAnalysisViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing WhatsApp chat analyses
    """
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_queryset(self):
        return ChatAnalysis.objects.filter(user=self.request.user).order_by('-created_at')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ChatAnalysisCreateSerializer
        elif self.action == 'list':
            return ChatAnalysisListSerializer
        else:
            return ChatAnalysisDetailSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Upload and process WhatsApp chat file
        """
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # For demo, process synchronously (in production, use Celery)
            chat_analysis = self._process_chat_sync(serializer)
            
            response_serializer = ChatAnalysisDetailSerializer(chat_analysis)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error creating chat analysis: {e}")
            return Response({
                'error': 'Failed to process chat file',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def _process_chat_sync(self, serializer):
        """
        Synchronous chat processing for demo
        """
        file = serializer.validated_data['file']
        user = self.request.user
        
        # Read file content
        file_content = file.read().decode('utf-8')
        
        # Create chat analysis
        chat_analysis = ChatAnalysis.objects.create(
            user=user,
            title=serializer.validated_data.get('title', file.name),
            original_filename=file.name,
            file_size=file.size,
            file_hash='demo_hash',
            status='processing',
            processing_started_at=timezone.now(),
            anonymize_participants=serializer.validated_data.get('anonymize_participants', True)
        )
        
        try:
            # Process chat
            preprocessor = WhatsAppChatPreprocessor()
            analyzer = MultiModelSentimentAnalyzer(use_transformers=False)  # Use basic models for demo
            analyzer.load_models()
            
            # Preprocess
            result = preprocessor.preprocess(file_content, chat_analysis.anonymize_participants)
            
            if not result['success']:
                raise Exception(result['error'])
            
            df = result['dataframe']
            summary = result['summary']
            
            # Update chat analysis
            chat_analysis.total_messages = summary['total_messages']
            chat_analysis.total_participants = summary['total_participants']
            chat_analysis.date_range_start = summary['date_range_start']
            chat_analysis.date_range_end = summary['date_range_end']
            chat_analysis.detected_language = list(summary['detected_languages'].keys())[0] if summary['detected_languages'] else 'unknown'
            
            # Create participants
            participants_map = {}
            for username, anonymized_name in summary['participant_mapping'].items():
                if username != 'System':
                    participant_data = df[df['username'] == username]
                    
                    participant = ChatParticipant.objects.create(
                        chat_analysis=chat_analysis,
                        original_name=username,
                        anonymized_name=anonymized_name,
                        participant_id=f"user_{len(participants_map) + 1}",
                        message_count=len(participant_data),
                        word_count=participant_data['word_count'].sum() if 'word_count' in participant_data else 0,
                        first_message_date=participant_data['timestamp'].min() if not participant_data.empty else None,
                        last_message_date=participant_data['timestamp'].max() if not participant_data.empty else None,
                    )
                    participants_map[username] = participant
            
            # Process messages (sample for demo)
            sentiment_scores = []
            sample_size = min(100, len(df))  # Process first 100 messages for demo
            
            for idx, row in df.head(sample_size).iterrows():
                if row['username'] in participants_map:
                    participant = participants_map[row['username']]
                    
                    # Analyze sentiment
                    if row['cleaned_text'] and row['cleaned_text'].strip():
                        analysis_result = analyzer.analyze_text(row['cleaned_text'], row.get('language', 'en'))
                        ensemble_sentiment = analysis_result.get('ensemble_sentiment', {})
                    else:
                        ensemble_sentiment = {'score': 0.0, 'label': 'neutral', 'confidence': 0.0}
                    
                    message = ChatMessage.objects.create(
                        chat_analysis=chat_analysis,
                        participant=participant,
                        message_type=row.get('message_type', 'text'),
                        original_text=row['original_text'],
                        cleaned_text=row.get('cleaned_text', ''),
                        word_count=row.get('word_count', 0),
                        timestamp=row['timestamp'],
                        hour=row.get('hour', 0),
                        day_of_week=row.get('day_of_week', 0),
                        sentiment_score=ensemble_sentiment.get('score'),
                        sentiment_label=ensemble_sentiment.get('label'),
                        sentiment_confidence=ensemble_sentiment.get('confidence'),
                        language_detected=row.get('language', 'unknown'),
                        contains_emoji=row.get('contains_emoji', False),
                        emoji_count=row.get('emoji_count', 0),
                        contains_url=row.get('contains_url', False),
                        url_count=row.get('url_count', 0),
                    )
                    
                    if ensemble_sentiment.get('score') is not None:
                        sentiment_scores.append(ensemble_sentiment['score'])
            
            # Calculate overall statistics
            if sentiment_scores:
                chat_analysis.overall_sentiment_score = sum(sentiment_scores) / len(sentiment_scores)
                
                positive_count = sum(1 for score in sentiment_scores if score > 0.1)
                negative_count = sum(1 for score in sentiment_scores if score < -0.1)
                
                if positive_count > negative_count:
                    chat_analysis.overall_sentiment_label = 'positive'
                elif negative_count > positive_count:
                    chat_analysis.overall_sentiment_label = 'negative'
                else:
                    chat_analysis.overall_sentiment_label = 'neutral'
            
            # Mark as completed
            chat_analysis.status = 'completed'
            chat_analysis.processing_completed_at = timezone.now()
            chat_analysis.processing_duration = (
                chat_analysis.processing_completed_at - chat_analysis.processing_started_at
            )
            chat_analysis.save()
            
            logger.info(f"Successfully processed chat analysis {chat_analysis.id}")
            return chat_analysis
            
        except Exception as e:
            chat_analysis.status = 'failed'
            chat_analysis.error_message = str(e)
            chat_analysis.save()
            raise e
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """
        Get messages for a chat analysis with filtering
        """
        chat_analysis = self.get_object()
        
        # Apply filters
        filter_serializer = MessageFilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        filters = filter_serializer.validated_data
        
        queryset = ChatMessage.objects.filter(chat_analysis=chat_analysis)
        
        # Apply filters
        if 'participant' in filters:
            queryset = queryset.filter(participant__anonymized_name=filters['participant'])
        
        if 'sentiment_label' in filters:
            queryset = queryset.filter(sentiment_label=filters['sentiment_label'])
        
        if 'emotion' in filters:
            queryset = queryset.filter(dominant_emotion=filters['emotion'])
        
        if 'date_from' in filters:
            queryset = queryset.filter(timestamp__gte=filters['date_from'])
        
        if 'date_to' in filters:
            queryset = queryset.filter(timestamp__lte=filters['date_to'])
        
        if 'min_sentiment_score' in filters:
            queryset = queryset.filter(sentiment_score__gte=filters['min_sentiment_score'])
        
        if 'max_sentiment_score' in filters:
            queryset = queryset.filter(sentiment_score__lte=filters['max_sentiment_score'])
        
        if 'contains_emoji' in filters:
            queryset = queryset.filter(contains_emoji=filters['contains_emoji'])
        
        if 'contains_url' in filters:
            queryset = queryset.filter(contains_url=filters['contains_url'])
        
        if 'message_type' in filters:
            queryset = queryset.filter(message_type=filters['message_type'])
        
        if 'search_text' in filters:
            queryset = queryset.filter(
                Q(original_text__icontains=filters['search_text']) |
                Q(cleaned_text__icontains=filters['search_text'])
            )
        
        # Paginate results
        page = self.paginate_queryset(queryset.order_by('timestamp'))
        if page is not None:
            serializer = ChatMessageSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ChatMessageSerializer(queryset.order_by('timestamp'), many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def participants(self, request, pk=None):
        """
        Get participants for a chat analysis
        """
        chat_analysis = self.get_object()
        participants = ChatParticipant.objects.filter(chat_analysis=chat_analysis)
        serializer = ChatParticipantSerializer(participants, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """
        Get detailed statistics for a chat analysis
        """
        chat_analysis = self.get_object()
        
        # Message statistics
        messages = ChatMessage.objects.filter(chat_analysis=chat_analysis)
        
        stats = {
            'overview': {
                'total_messages': messages.count(),
                'total_participants': chat_analysis.participants.count(),
                'date_range': {
                    'start': chat_analysis.date_range_start,
                    'end': chat_analysis.date_range_end
                },
                'processing_time': chat_analysis.processing_duration.total_seconds() if chat_analysis.processing_duration else None
            },
            'sentiment': {
                'overall_score': chat_analysis.overall_sentiment_score,
                'overall_label': chat_analysis.overall_sentiment_label,
                'distribution': messages.values('sentiment_label').annotate(count=Count('id')).order_by('sentiment_label')
            },
            'activity': {
                'by_hour': messages.values('hour').annotate(count=Count('id')).order_by('hour'),
                'by_day': messages.values('day_of_week').annotate(count=Count('id')).order_by('day_of_week'),
                'by_participant': chat_analysis.participants.values('anonymized_name', 'message_count').order_by('-message_count')
            },
            'content': {
                'message_types': messages.values('message_type').annotate(count=Count('id')),
                'languages': messages.values('language_detected').annotate(count=Count('id')),
                'emoji_usage': {
                    'messages_with_emoji': messages.filter(contains_emoji=True).count(),
                    'total_emojis': messages.aggregate(total=Count('emoji_count'))['total'] or 0
                },
                'url_sharing': {
                    'messages_with_urls': messages.filter(contains_url=True).count(),
                    'total_urls': messages.aggregate(total=Count('url_count'))['total'] or 0
                }
            }
        }
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def user_stats(self, request):
        """
        Get user's overall statistics
        """
        user_analyses = self.get_queryset()
        
        stats = {
            'total_analyses': user_analyses.count(),
            'completed_analyses': user_analyses.filter(status='completed').count(),
            'processing_analyses': user_analyses.filter(status__in=['pending', 'processing']).count(),
            'failed_analyses': user_analyses.filter(status='failed').count(),
            'total_messages_processed': user_analyses.aggregate(
                total=Count('messages')
            )['total'] or 0,
            'recent_analyses': ChatAnalysisListSerializer(
                user_analyses[:5], many=True
            ).data
        }
        
        return Response(stats)