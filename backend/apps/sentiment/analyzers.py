"""
Advanced sentiment and emotion analysis module
Production-ready with multiple models and error handling
"""
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union
from abc import ABC, abstractmethod
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import asyncio

# Sentiment analysis libraries
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob

# Deep learning libraries
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logging.warning("Transformers library not available. Some models will be disabled.")

# Language detection
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException

# Set seed for consistent results
DetectorFactory.seed = 0

logger = logging.getLogger(__name__)


class BaseSentimentAnalyzer(ABC):
    """
    Abstract base class for sentiment analyzers
    """
    
    def __init__(self, name: str, supported_languages: List[str] = None):
        self.name = name
        self.supported_languages = supported_languages or ['en']
        self.is_loaded = False
        self.load_time = None
    
    @abstractmethod
    def load_model(self):
        """Load the sentiment analysis model"""
        pass
    
    @abstractmethod
    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """
        Analyze sentiment of text
        Returns: {'score': float, 'label': str, 'confidence': float}
        """
        pass
    
    def is_language_supported(self, language: str) -> bool:
        """Check if language is supported"""
        return language in self.supported_languages
    
    def preprocess_text(self, text: str) -> str:
        """Preprocess text before analysis"""
        if not text or not isinstance(text, str):
            return ""
        return text.strip()


class VADERAnalyzer(BaseSentimentAnalyzer):
    """
    VADER (Valence Aware Dictionary and sEntiment Reasoner) analyzer
    Good for social media text, handles emojis and slang
    """
    
    def __init__(self):
        super().__init__("VADER", ["en", "hinglish"])
        self.analyzer = None
    
    def load_model(self):
        """Load VADER model"""
        try:
            start_time = time.time()
            self.analyzer = SentimentIntensityAnalyzer()
            self.load_time = time.time() - start_time
            self.is_loaded = True
            logger.info(f"VADER model loaded in {self.load_time:.2f} seconds")
        except Exception as e:
            logger.error(f"Failed to load VADER model: {e}")
            raise
    
    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """Analyze sentiment using VADER"""
        if not self.is_loaded:
            self.load_model()
        
        text = self.preprocess_text(text)
        if not text:
            return {'score': 0.0, 'label': 'neutral', 'confidence': 0.0}
        
        try:
            scores = self.analyzer.polarity_scores(text)
            compound_score = scores['compound']
            
            # Determine label based on compound score
            if compound_score >= 0.05:
                label = 'positive'
            elif compound_score <= -0.05:
                label = 'negative'
            else:
                label = 'neutral'
            
            # Calculate confidence based on the absolute value
            confidence = abs(compound_score)
            
            return {
                'score': compound_score,
                'label': label,
                'confidence': confidence,
                'detailed_scores': {
                    'positive': scores['pos'],
                    'negative': scores['neg'],
                    'neutral': scores['neu']
                }
            }
        except Exception as e:
            logger.error(f"VADER analysis failed: {e}")
            return {'score': 0.0, 'label': 'neutral', 'confidence': 0.0}


class TextBlobAnalyzer(BaseSentimentAnalyzer):
    """
    TextBlob sentiment analyzer
    Simple and fast, good baseline
    """
    
    def __init__(self):
        super().__init__("TextBlob", ["en"])
    
    def load_model(self):
        """TextBlob doesn't require explicit model loading"""
        self.is_loaded = True
        logger.info("TextBlob analyzer ready")
    
    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """Analyze sentiment using TextBlob"""
        if not self.is_loaded:
            self.load_model()
        
        text = self.preprocess_text(text)
        if not text:
            return {'score': 0.0, 'label': 'neutral', 'confidence': 0.0}
        
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity  # -1 to 1
            subjectivity = blob.sentiment.subjectivity  # 0 to 1
            
            # Determine label
            if polarity > 0.1:
                label = 'positive'
            elif polarity < -0.1:
                label = 'negative'
            else:
                label = 'neutral'
            
            # Use subjectivity as confidence measure
            confidence = subjectivity
            
            return {
                'score': polarity,
                'label': label,
                'confidence': confidence,
                'subjectivity': subjectivity
            }
        except Exception as e:
            logger.error(f"TextBlob analysis failed: {e}")
            return {'score': 0.0, 'label': 'neutral', 'confidence': 0.0}


class TransformerAnalyzer(BaseSentimentAnalyzer):
    """
    Transformer-based sentiment analyzer (RoBERTa, BERT, etc.)
    High accuracy but slower
    """
    
    def __init__(self, model_name: str = "cardiffnlp/twitter-roberta-base-sentiment-latest"):
        super().__init__("Transformer", ["en"])
        self.model_name = model_name
        self.pipeline = None
    
    def load_model(self):
        """Load transformer model"""
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError("Transformers library not available")
        
        try:
            start_time = time.time()
            self.pipeline = pipeline(
                "sentiment-analysis",
                model=self.model_name,
                tokenizer=self.model_name,
                return_all_scores=True
            )
            self.load_time = time.time() - start_time
            self.is_loaded = True
            logger.info(f"Transformer model {self.model_name} loaded in {self.load_time:.2f} seconds")
        except Exception as e:
            logger.error(f"Failed to load transformer model: {e}")
            raise
    
    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """Analyze sentiment using transformer model"""
        if not self.is_loaded:
            self.load_model()
        
        text = self.preprocess_text(text)
        if not text:
            return {'score': 0.0, 'label': 'neutral', 'confidence': 0.0}
        
        try:
            # Truncate text if too long
            if len(text) > 512:
                text = text[:512]
            
            results = self.pipeline(text)[0]
            
            # Convert to standard format
            label_map = {
                'POSITIVE': 'positive',
                'NEGATIVE': 'negative',
                'NEUTRAL': 'neutral',
                'LABEL_0': 'negative',
                'LABEL_1': 'neutral',
                'LABEL_2': 'positive'
            }
            
            # Find the highest scoring result
            best_result = max(results, key=lambda x: x['score'])
            label = label_map.get(best_result['label'], best_result['label'].lower())
            confidence = best_result['score']
            
            # Convert to -1 to 1 scale
            if label == 'positive':
                score = confidence
            elif label == 'negative':
                score = -confidence
            else:
                score = 0.0
            
            return {
                'score': score,
                'label': label,
                'confidence': confidence,
                'all_scores': {result['label']: result['score'] for result in results}
            }
        except Exception as e:
            logger.error(f"Transformer analysis failed: {e}")
            return {'score': 0.0, 'label': 'neutral', 'confidence': 0.0}


class EmotionAnalyzer:
    """
    Emotion detection analyzer
    Detects basic emotions: joy, sadness, anger, fear, surprise, disgust
    """
    
    def __init__(self, model_name: str = "j-hartmann/emotion-english-distilroberta-base"):
        self.model_name = model_name
        self.pipeline = None
        self.is_loaded = False
        self.emotions = ['joy', 'sadness', 'anger', 'fear', 'surprise', 'disgust']
    
    def load_model(self):
        """Load emotion detection model"""
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError("Transformers library not available")
        
        try:
            start_time = time.time()
            self.pipeline = pipeline(
                "text-classification",
                model=self.model_name,
                tokenizer=self.model_name,
                return_all_scores=True
            )
            load_time = time.time() - start_time
            self.is_loaded = True
            logger.info(f"Emotion model loaded in {load_time:.2f} seconds")
        except Exception as e:
            logger.error(f"Failed to load emotion model: {e}")
            raise
    
    def analyze_emotion(self, text: str) -> Dict[str, float]:
        """Analyze emotions in text"""
        if not self.is_loaded:
            self.load_model()
        
        if not text or not isinstance(text, str):
            return {emotion: 0.0 for emotion in self.emotions}
        
        try:
            # Truncate text if too long
            if len(text) > 512:
                text = text[:512]
            
            results = self.pipeline(text)[0]
            
            # Convert to emotion scores
            emotion_scores = {}
            dominant_emotion = None
            max_score = 0.0
            
            for result in results:
                emotion = result['label'].lower()
                score = result['score']
                emotion_scores[emotion] = score
                
                if score > max_score:
                    max_score = score
                    dominant_emotion = emotion
            
            return {
                'emotion_scores': emotion_scores,
                'dominant_emotion': dominant_emotion,
                'confidence': max_score
            }
        except Exception as e:
            logger.error(f"Emotion analysis failed: {e}")
            return {
                'emotion_scores': {emotion: 0.0 for emotion in self.emotions},
                'dominant_emotion': 'neutral',
                'confidence': 0.0
            }


class ToxicityAnalyzer:
    """
    Toxicity detection analyzer
    Detects harmful, toxic, or inappropriate content
    """
    
    def __init__(self, model_name: str = "unitary/toxic-bert"):
        self.model_name = model_name
        self.pipeline = None
        self.is_loaded = False
    
    def load_model(self):
        """Load toxicity detection model"""
        if not TRANSFORMERS_AVAILABLE:
            logger.warning("Transformers not available, using rule-based toxicity detection")
            self.is_loaded = True
            return
        
        try:
            start_time = time.time()
            self.pipeline = pipeline(
                "text-classification",
                model=self.model_name,
                tokenizer=self.model_name
            )
            load_time = time.time() - start_time
            self.is_loaded = True
            logger.info(f"Toxicity model loaded in {load_time:.2f} seconds")
        except Exception as e:
            logger.warning(f"Failed to load toxicity model, using rule-based: {e}")
            self.is_loaded = True
    
    def analyze_toxicity(self, text: str) -> Dict[str, float]:
        """Analyze toxicity in text"""
        if not self.is_loaded:
            self.load_model()
        
        if not text or not isinstance(text, str):
            return {'toxicity_score': 0.0, 'is_toxic': False}
        
        try:
            if self.pipeline:
                # Use ML model
                if len(text) > 512:
                    text = text[:512]
                
                result = self.pipeline(text)[0]
                
                if result['label'] == 'TOXIC':
                    toxicity_score = result['score']
                    is_toxic = toxicity_score > 0.5
                else:
                    toxicity_score = 1 - result['score']
                    is_toxic = False
            else:
                # Use rule-based approach
                toxicity_score, is_toxic = self._rule_based_toxicity(text)
            
            return {
                'toxicity_score': toxicity_score,
                'is_toxic': is_toxic
            }
        except Exception as e:
            logger.error(f"Toxicity analysis failed: {e}")
            return {'toxicity_score': 0.0, 'is_toxic': False}
    
    def _rule_based_toxicity(self, text: str) -> Tuple[float, bool]:
        """Simple rule-based toxicity detection"""
        toxic_words = [
            'hate', 'stupid', 'idiot', 'kill', 'die', 'death',
            # Add more toxic words as needed
        ]
        
        text_lower = text.lower()
        toxic_count = sum(1 for word in toxic_words if word in text_lower)
        
        # Simple scoring based on toxic word count
        toxicity_score = min(toxic_count * 0.3, 1.0)
        is_toxic = toxicity_score > 0.5
        
        return toxicity_score, is_toxic


class MultiModelSentimentAnalyzer:
    """
    Ensemble analyzer that combines multiple sentiment analysis models
    """
    
    def __init__(self, use_transformers: bool = True):
        self.analyzers = {}
        self.emotion_analyzer = None
        self.toxicity_analyzer = None
        self.use_transformers = use_transformers and TRANSFORMERS_AVAILABLE
        
        # Initialize analyzers
        self._initialize_analyzers()
    
    def _initialize_analyzers(self):
        """Initialize all sentiment analyzers"""
        try:
            # Always available analyzers
            self.analyzers['vader'] = VADERAnalyzer()
            self.analyzers['textblob'] = TextBlobAnalyzer()
            
            # Transformer-based analyzers (if available)
            if self.use_transformers:
                self.analyzers['roberta'] = TransformerAnalyzer()
                self.emotion_analyzer = EmotionAnalyzer()
                self.toxicity_analyzer = ToxicityAnalyzer()
            
            logger.info(f"Initialized {len(self.analyzers)} sentiment analyzers")
        except Exception as e:
            logger.error(f"Failed to initialize analyzers: {e}")
    
    def load_models(self):
        """Load all models"""
        for name, analyzer in self.analyzers.items():
            try:
                analyzer.load_model()
                logger.info(f"Loaded {name} analyzer")
            except Exception as e:
                logger.error(f"Failed to load {name} analyzer: {e}")
        
        if self.emotion_analyzer:
            try:
                self.emotion_analyzer.load_model()
            except Exception as e:
                logger.error(f"Failed to load emotion analyzer: {e}")
        
        if self.toxicity_analyzer:
            try:
                self.toxicity_analyzer.load_model()
            except Exception as e:
                logger.error(f"Failed to load toxicity analyzer: {e}")
    
    def analyze_text(self, text: str, language: str = 'en') -> Dict:
        """
        Comprehensive text analysis including sentiment, emotion, and toxicity
        """
        if not text or not isinstance(text, str):
            return self._empty_result()
        
        results = {
            'text': text,
            'language': language,
            'sentiment_results': {},
            'emotion_results': {},
            'toxicity_results': {},
            'ensemble_sentiment': {},
            'processing_time': 0.0
        }
        
        start_time = time.time()
        
        try:
            # Sentiment analysis with multiple models
            sentiment_scores = []
            sentiment_labels = []
            
            for name, analyzer in self.analyzers.items():
                if analyzer.is_language_supported(language):
                    try:
                        result = analyzer.analyze_sentiment(text)
                        results['sentiment_results'][name] = result
                        
                        if result.get('score') is not None:
                            sentiment_scores.append(result['score'])
                            sentiment_labels.append(result['label'])
                    except Exception as e:
                        logger.error(f"Error in {name} analysis: {e}")
            
            # Ensemble sentiment (average of all models)
            if sentiment_scores:
                ensemble_score = np.mean(sentiment_scores)
                ensemble_label = max(set(sentiment_labels), key=sentiment_labels.count)
                ensemble_confidence = np.std(sentiment_scores)  # Lower std = higher confidence
                
                results['ensemble_sentiment'] = {
                    'score': ensemble_score,
                    'label': ensemble_label,
                    'confidence': 1.0 - min(ensemble_confidence, 1.0),
                    'model_agreement': len(set(sentiment_labels)) == 1
                }
            
            # Emotion analysis
            if self.emotion_analyzer:
                try:
                    emotion_result = self.emotion_analyzer.analyze_emotion(text)
                    results['emotion_results'] = emotion_result
                except Exception as e:
                    logger.error(f"Error in emotion analysis: {e}")
            
            # Toxicity analysis
            if self.toxicity_analyzer:
                try:
                    toxicity_result = self.toxicity_analyzer.analyze_toxicity(text)
                    results['toxicity_results'] = toxicity_result
                except Exception as e:
                    logger.error(f"Error in toxicity analysis: {e}")
            
            results['processing_time'] = time.time() - start_time
            
        except Exception as e:
            logger.error(f"Error in comprehensive analysis: {e}")
            results['error'] = str(e)
        
        return results
    
    def analyze_batch(self, texts: List[str], language: str = 'en', max_workers: int = 4) -> List[Dict]:
        """
        Analyze multiple texts in parallel
        """
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_text = {
                executor.submit(self.analyze_text, text, language): text 
                for text in texts
            }
            
            for future in as_completed(future_to_text):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.error(f"Error in batch analysis: {e}")
                    results.append(self._empty_result())
        
        return results
    
    def _empty_result(self) -> Dict:
        """Return empty result structure"""
        return {
            'text': '',
            'language': 'unknown',
            'sentiment_results': {},
            'emotion_results': {},
            'toxicity_results': {},
            'ensemble_sentiment': {'score': 0.0, 'label': 'neutral', 'confidence': 0.0},
            'processing_time': 0.0
        }
    
    def get_model_info(self) -> Dict:
        """Get information about loaded models"""
        info = {
            'sentiment_models': {},
            'emotion_model': None,
            'toxicity_model': None,
            'total_models': len(self.analyzers)
        }
        
        for name, analyzer in self.analyzers.items():
            info['sentiment_models'][name] = {
                'name': analyzer.name,
                'supported_languages': analyzer.supported_languages,
                'is_loaded': analyzer.is_loaded,
                'load_time': analyzer.load_time
            }
        
        if self.emotion_analyzer:
            info['emotion_model'] = {
                'name': self.emotion_analyzer.model_name,
                'is_loaded': self.emotion_analyzer.is_loaded,
                'emotions': self.emotion_analyzer.emotions
            }
        
        if self.toxicity_analyzer:
            info['toxicity_model'] = {
                'name': self.toxicity_analyzer.model_name,
                'is_loaded': self.toxicity_analyzer.is_loaded
            }
        
        return info