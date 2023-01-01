"""
Sentiment analysis API views
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .analyzers import MultiModelSentimentAnalyzer
import logging

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def model_info(request):
    """
    Get information about available sentiment analysis models
    """
    try:
        analyzer = MultiModelSentimentAnalyzer(use_transformers=False)
        info = analyzer.get_model_info()
        return Response(info, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error getting model info: {e}")
        return Response({
            'error': 'Failed to get model information',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyze_text(request):
    """
    Analyze sentiment of provided text
    """
    try:
        text = request.data.get('text', '')
        language = request.data.get('language', 'en')
        
        if not text:
            return Response({
                'error': 'Text is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        analyzer = MultiModelSentimentAnalyzer(use_transformers=False)
        analyzer.load_models()
        
        result = analyzer.analyze_text(text, language)
        
        return Response(result, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error analyzing text: {e}")
        return Response({
            'error': 'Failed to analyze text',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)