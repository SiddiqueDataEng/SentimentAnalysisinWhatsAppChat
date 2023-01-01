"""
Analytics views for WhatsApp Sentiment Analysis
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
import logging

from apps.chat_analysis.models import ChatAnalysis, ChatMessage, ChatParticipant

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_analytics_overview(request):
    """
    Get user's analytics overview
    """
    try:
        user = request.user
        
        # Get user's analyses
        analyses = ChatAnalysis.objects.filter(user=user, status='completed')
        
        # Calculate statistics
        total_analyses = analyses.count()
        total_messages = sum(analysis.total_messages for analysis in analyses)
        
        # Sentiment distribution
        sentiment_stats = ChatMessage.objects.filter(
            chat_analysis__user=user,
            sentiment_label__isnull=False
        ).values('sentiment_label').annotate(count=Count('id'))
        
        # Recent activity (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_analyses = analyses.filter(created_at__gte=thirty_days_ago).count()
        
        return Response({
            'total_analyses': total_analyses,
            'total_messages_processed': total_messages,
            'recent_analyses': recent_analyses,
            'sentiment_distribution': list(sentiment_stats),
            'avg_processing_time': analyses.aggregate(
                avg_time=Avg('processing_duration')
            )['avg_time']
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error getting user analytics: {e}")
        return Response({
            'error': 'Failed to get analytics data'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sentiment_trends(request, analysis_id):
    """
    Get sentiment trends for a specific analysis
    """
    try:
        analysis = ChatAnalysis.objects.get(id=analysis_id, user=request.user)
        
        # Get messages grouped by hour/day
        messages = ChatMessage.objects.filter(
            chat_analysis=analysis,
            sentiment_score__isnull=False
        ).order_by('timestamp')
        
        # Group by hour for trend analysis
        hourly_sentiment = messages.extra({
            'hour': "date_trunc('hour', timestamp)"
        }).values('hour').annotate(
            avg_sentiment=Avg('sentiment_score'),
            message_count=Count('id')
        ).order_by('hour')
        
        return Response({
            'analysis_id': str(analysis_id),
            'hourly_trends': list(hourly_sentiment),
            'overall_sentiment': analysis.overall_sentiment_score,
            'total_messages': messages.count()
        }, status=status.HTTP_200_OK)
        
    except ChatAnalysis.DoesNotExist:
        return Response({
            'error': 'Analysis not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error getting sentiment trends: {e}")
        return Response({
            'error': 'Failed to get sentiment trends'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)