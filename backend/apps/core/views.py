"""
Core views for health checks and error handling
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Health check endpoint for monitoring
    """
    try:
        from django.db import connection
        from django.core.cache import cache
        
        # Check database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        # Check Redis connection
        cache.set('health_check', 'ok', 10)
        cache_status = cache.get('health_check')
        
        return Response({
            'status': 'healthy',
            'database': 'connected',
            'cache': 'connected' if cache_status == 'ok' else 'disconnected',
            'debug': settings.DEBUG,
            'version': '1.0.0'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return Response({
            'status': 'unhealthy',
            'error': str(e)
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)


@api_view(['GET'])
@permission_classes([AllowAny])
def system_info(request):
    """
    System information endpoint
    """
    try:
        import sys
        import django
        from apps.sentiment.analyzers import MultiModelSentimentAnalyzer
        
        # Get ML model info
        analyzer = MultiModelSentimentAnalyzer(use_transformers=False)  # Quick check
        model_info = analyzer.get_model_info()
        
        return Response({
            'python_version': sys.version,
            'django_version': django.get_version(),
            'ml_models': model_info,
            'debug_mode': settings.DEBUG,
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"System info failed: {e}")
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def custom_404(request, exception=None):
    """Custom 404 error handler"""
    return JsonResponse({
        'error': 'Not Found',
        'message': 'The requested resource was not found.',
        'status_code': 404
    }, status=404)


def custom_500(request):
    """Custom 500 error handler"""
    return JsonResponse({
        'error': 'Internal Server Error',
        'message': 'An internal server error occurred.',
        'status_code': 500
    }, status=500)