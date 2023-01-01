"""
Celery tasks for WhatsApp chat analysis
"""
from celery import shared_task
from django.utils import timezone
from django.contrib.auth import get_user_model
import logging
import time
from datetime import timedelta

from .models import ChatAnalysis, ChatParticipant, ChatMessage
from .preprocessing import WhatsAppChatPreprocessor
from apps.sentiment.analyzers import MultiModelSentimentAnalyzer

User = get_user_model()
logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def process_whatsapp_chat(self, chat_analysis_id: str, file_content: str):
    """
    Process WhatsApp chat file and perform sentiment analysis
    """
    try:
        # Get chat analysis object
        chat_analysis = ChatAnalysis.objects.get(id=chat_analysis_id)
        chat_analysis.status = 'processing'
        chat_analysis.processing_started_at = timezone.now()
        chat_analysis.save()
        
        logger.info(f"Starting processing for chat analysis {chat_analysis_id}")
        
        # Initialize preprocessor and analyzer
        preprocessor = WhatsAppChatPreprocessor()
        analyzer = MultiModelSentimentAnalyzer()
        analyzer.load_models()
        
        # Preprocess chat data
        preprocessing_result = preprocessor.preprocess(
            file_content, 
            anonymize=chat_analysis.anonymize_participants
        )
        
        if not preprocessing_result['success']:
            raise Exception(f"Preprocessing failed: {preprocessing_result['error']}")
        
        df = preprocessing_result['dataframe']
        summary = preprocessing_result['summary']
        
        # Update chat analysis with summary info
        chat_analysis.total_messages = summary['total_messages']
        chat_analysis.total_participants = summary['total_participants']
        chat_analysis.date_range_start = summary['date_range_start']
        chat_analysis.date_range_end = summary['date_range_end']
        chat_analysis.detected_language = _get_dominant_language(summary['detected_languages'])
        chat_analysis.save()
        
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
                    word_count=participant_data['word_count'].sum(),
                    first_message_date=participant_data['timestamp'].min(),
                    last_message_date=participant_data['timestamp'].max(),
                    most_active_hour=participant_data['hour'].mode().iloc[0] if not participant_data.empty else None,
                    most_active_day=participant_data['day_of_week'].mode().iloc[0] if not participant_data.empty else None,
                )
                participants_map[username] = participant
        
        # Process messages in batches
        batch_size = 100
        total_messages = len(df)
        processed_messages = 0
        
        sentiment_scores = []
        emotion_data = []
        toxicity_scores = []
        
        for i in range(0, total_messages, batch_size):
            batch_df = df.iloc[i:i + batch_size]
            
            # Prepare texts for batch analysis
            texts = batch_df['cleaned_text'].tolist()
            languages = batch_df['language'].tolist()
            
            # Perform batch sentiment analysis
            batch_results = []
            for text, lang in zip(texts, languages):
                if text and text.strip():
                    result = analyzer.analyze_text(text, lang)
                    batch_results.append(result)
                else:
                    batch_results.append(analyzer._empty_result())
            
            # Create ChatMessage objects
            messages_to_create = []
            for idx, (_, row) in enumerate(batch_df.iterrows()):
                if row['username'] in participants_map:
                    participant = participants_map[row['username']]
                    analysis_result = batch_results[idx]
                    
                    # Extract sentiment data
                    ensemble_sentiment = analysis_result.get('ensemble_sentiment', {})
                    emotion_results = analysis_result.get('emotion_results', {})
                    toxicity_results = analysis_result.get('toxicity_results', {})
                    
                    message = ChatMessage(
                        chat_analysis=chat_analysis,
                        participant=participant,
                        message_type=row['message_type'],
                        original_text=row['original_text'],
                        cleaned_text=row['cleaned_text'],
                        word_count=row['word_count'],
                        timestamp=row['timestamp'],
                        hour=row['hour'],
                        day_of_week=row['day_of_week'],
                        sentiment_score=ensemble_sentiment.get('score'),
                        sentiment_label=ensemble_sentiment.get('label'),
                        sentiment_confidence=ensemble_sentiment.get('confidence'),
                        emotion_scores=emotion_results.get('emotion_scores', {}),
                        dominant_emotion=emotion_results.get('dominant_emotion'),
                        emotion_confidence=emotion_results.get('confidence'),
                        toxicity_score=toxicity_results.get('toxicity_score'),
                        language_detected=row['language'],
                        contains_emoji=row['contains_emoji'],
                        emoji_count=row['emoji_count'],
                        contains_url=row['contains_url'],
                        url_count=row['url_count'],
                    )
                    messages_to_create.append(message)
                    
                    # Collect data for overall statistics
                    if ensemble_sentiment.get('score') is not None:
                        sentiment_scores.append(ensemble_sentiment['score'])
                    
                    if emotion_results.get('dominant_emotion'):
                        emotion_data.append(emotion_results['dominant_emotion'])
                    
                    if toxicity_results.get('toxicity_score') is not None:
                        toxicity_scores.append(toxicity_results['toxicity_score'])
            
            # Bulk create messages
            ChatMessage.objects.bulk_create(messages_to_create, batch_size=batch_size)
            
            processed_messages += len(messages_to_create)
            
            # Update progress
            progress = (processed_messages / total_messages) * 100
            self.update_state(
                state='PROGRESS',
                meta={'current': processed_messages, 'total': total_messages, 'progress': progress}
            )
            
            logger.info(f"Processed {processed_messages}/{total_messages} messages ({progress:.1f}%)")
        
        # Calculate overall statistics
        if sentiment_scores:
            chat_analysis.overall_sentiment_score = sum(sentiment_scores) / len(sentiment_scores)
            
            # Determine overall sentiment label
            positive_count = sum(1 for score in sentiment_scores if score > 0.1)
            negative_count = sum(1 for score in sentiment_scores if score < -0.1)
            
            if positive_count > negative_count:
                chat_analysis.overall_sentiment_label = 'positive'
            elif negative_count > positive_count:
                chat_analysis.overall_sentiment_label = 'negative'
            else:
                chat_analysis.overall_sentiment_label = 'neutral'
        
        if emotion_data:
            # Find most common emotion
            emotion_counts = {}
            for emotion in emotion_data:
                emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
            chat_analysis.dominant_emotion = max(emotion_counts, key=emotion_counts.get)
        
        if toxicity_scores:
            chat_analysis.toxicity_score = sum(toxicity_scores) / len(toxicity_scores)
        
        # Update participant statistics
        for participant in participants_map.values():
            participant_messages = ChatMessage.objects.filter(participant=participant)
            
            # Calculate average sentiment
            sentiment_scores = participant_messages.filter(
                sentiment_score__isnull=False
            ).values_list('sentiment_score', flat=True)
            
            if sentiment_scores:
                participant.avg_sentiment_score = sum(sentiment_scores) / len(sentiment_scores)
            
            # Find dominant emotion
            emotions = participant_messages.filter(
                dominant_emotion__isnull=False
            ).values_list('dominant_emotion', flat=True)
            
            if emotions:
                emotion_counts = {}
                for emotion in emotions:
                    emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
                participant.dominant_emotion = max(emotion_counts, key=emotion_counts.get)
            
            participant.save()
        
        # Mark as completed
        chat_analysis.status = 'completed'
        chat_analysis.processing_completed_at = timezone.now()
        chat_analysis.processing_duration = (
            chat_analysis.processing_completed_at - chat_analysis.processing_started_at
        )
        chat_analysis.save()
        
        # Update user profile statistics
        user_profile = chat_analysis.user.profile
        user_profile.total_chats_analyzed += 1
        user_profile.total_messages_processed += total_messages
        user_profile.save()
        
        logger.info(f"Successfully completed processing for chat analysis {chat_analysis_id}")
        
        return {
            'status': 'completed',
            'total_messages': total_messages,
            'processing_time': chat_analysis.processing_duration.total_seconds(),
            'overall_sentiment': chat_analysis.overall_sentiment_label,
            'dominant_emotion': chat_analysis.dominant_emotion,
        }
        
    except Exception as exc:
        logger.error(f"Error processing chat analysis {chat_analysis_id}: {exc}")
        
        # Update chat analysis with error
        try:
            chat_analysis = ChatAnalysis.objects.get(id=chat_analysis_id)
            chat_analysis.status = 'failed'
            chat_analysis.error_message = str(exc)
            chat_analysis.processing_completed_at = timezone.now()
            chat_analysis.save()
        except:
            pass
        
        # Retry if not exceeded max retries
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying task in 60 seconds (attempt {self.request.retries + 1})")
            raise self.retry(countdown=60, exc=exc)
        
        raise exc


@shared_task
def cleanup_old_analyses():
    """
    Clean up old chat analyses (older than 30 days for free users)
    """
    try:
        cutoff_date = timezone.now() - timedelta(days=30)
        
        # Delete old analyses for free users
        old_analyses = ChatAnalysis.objects.filter(
            created_at__lt=cutoff_date,
            user__profile__subscription_type='free'
        )
        
        count = old_analyses.count()
        old_analyses.delete()
        
        logger.info(f"Cleaned up {count} old chat analyses")
        return {'cleaned_up': count}
        
    except Exception as e:
        logger.error(f"Error in cleanup task: {e}")
        raise


@shared_task
def generate_analysis_report(chat_analysis_id: str, report_type: str = 'summary'):
    """
    Generate analysis report for a chat
    """
    try:
        from .reports import ReportGenerator
        
        chat_analysis = ChatAnalysis.objects.get(id=chat_analysis_id)
        generator = ReportGenerator(chat_analysis)
        
        report = generator.generate_report(report_type)
        
        logger.info(f"Generated {report_type} report for chat analysis {chat_analysis_id}")
        return report
        
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        raise


def _get_dominant_language(language_counts: dict) -> str:
    """Get the dominant language from language counts"""
    if not language_counts:
        return 'unknown'
    
    # Remove 'unknown' from consideration if other languages exist
    filtered_counts = {k: v for k, v in language_counts.items() if k != 'unknown'}
    
    if filtered_counts:
        return max(filtered_counts, key=filtered_counts.get)
    else:
        return 'unknown'