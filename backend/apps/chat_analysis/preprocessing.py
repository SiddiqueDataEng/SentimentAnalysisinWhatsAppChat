"""
Enhanced WhatsApp chat preprocessing module
Production-ready with error handling and multiple format support
"""
import re
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import logging
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException
import emoji
from urlextract import URLExtract
import hashlib

# Set seed for consistent language detection
DetectorFactory.seed = 0

logger = logging.getLogger(__name__)


class WhatsAppChatPreprocessor:
    """
    Enhanced WhatsApp chat preprocessor with multiple format support
    """
    
    def __init__(self):
        self.url_extractor = URLExtract()
        self.supported_formats = ['android', 'ios', 'web']
        
        # Regex patterns for different WhatsApp export formats
        self.patterns = {
            'android': r'(\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2})\s-\s',
            'ios': r'\[(\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}:\d{2})\]\s',
            'web': r'(\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2})\s-\s',
        }
        
        # System message patterns
        self.system_patterns = [
            r'Messages and calls are end-to-end encrypted',
            r'created group',
            r'added you',
            r'left',
            r'joined using this group\'s invite link',
            r'changed the group description',
            r'changed the subject',
            r'You deleted this message',
            r'This message was deleted',
            r'<Media omitted>',
            r'image omitted',
            r'video omitted',
            r'audio omitted',
            r'document omitted',
            r'Contact card omitted',
            r'Location:',
        ]
        
        # Load stop words for different languages
        self.stop_words = self._load_stop_words()
    
    def _load_stop_words(self) -> Dict[str, set]:
        """Load stop words for different languages"""
        try:
            # You can load from files or use NLTK
            return {
                'english': set(),  # Load English stop words
                'hindi': set(),    # Load Hindi stop words
                'hinglish': set(), # Load Hinglish stop words
            }
        except Exception as e:
            logger.warning(f"Could not load stop words: {e}")
            return {}
    
    def detect_format(self, text: str) -> str:
        """
        Detect WhatsApp export format
        """
        for format_name, pattern in self.patterns.items():
            if re.search(pattern, text[:1000]):  # Check first 1000 chars
                return format_name
        
        logger.warning("Could not detect WhatsApp format, defaulting to Android")
        return 'android'
    
    def extract_messages_and_dates(self, text: str, format_type: str) -> Tuple[List[str], List[str]]:
        """
        Extract messages and dates based on format
        """
        pattern = self.patterns.get(format_type, self.patterns['android'])
        
        # Split text by pattern
        messages = re.split(pattern, text)[1:]  # Skip first empty element
        dates = re.findall(pattern, text)
        
        # Ensure equal length
        min_length = min(len(messages), len(dates))
        messages = messages[:min_length]
        dates = dates[:min_length]
        
        return messages, dates
    
    def parse_datetime(self, date_str: str, format_type: str) -> Optional[datetime]:
        """
        Parse datetime string based on format
        """
        try:
            # Remove extra characters
            date_str = date_str.strip(' -[]')
            
            # Common datetime formats
            formats = [
                '%d/%m/%Y, %H:%M',
                '%m/%d/%Y, %H:%M',
                '%d/%m/%y, %H:%M',
                '%m/%d/%y, %H:%M',
                '%d/%m/%Y, %H:%M:%S',
                '%m/%d/%Y, %H:%M:%S',
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            
            logger.warning(f"Could not parse datetime: {date_str}")
            return None
            
        except Exception as e:
            logger.error(f"Error parsing datetime {date_str}: {e}")
            return None
    
    def extract_user_and_message(self, message_text: str) -> Tuple[str, str]:
        """
        Extract username and message content
        """
        try:
            # Split by first colon followed by space
            parts = message_text.split(': ', 1)
            
            if len(parts) == 2:
                username = parts[0].strip()
                message = parts[1].strip()
                
                # Clean username (remove phone numbers, special chars)
                username = re.sub(r'\+\d+', '', username).strip()
                username = re.sub(r'[^\w\s-]', '', username).strip()
                
                return username, message
            else:
                # System message or malformed message
                return 'System', message_text.strip()
                
        except Exception as e:
            logger.error(f"Error extracting user and message: {e}")
            return 'Unknown', message_text
    
    def is_system_message(self, message: str) -> bool:
        """
        Check if message is a system message
        """
        message_lower = message.lower()
        return any(pattern.lower() in message_lower for pattern in self.system_patterns)
    
    def detect_language(self, text: str) -> str:
        """
        Detect message language
        """
        try:
            if not text or len(text.strip()) < 3:
                return 'unknown'
            
            # Remove URLs and emojis for better detection
            clean_text = self.clean_text_for_analysis(text)
            
            if len(clean_text.strip()) < 3:
                return 'unknown'
            
            detected = detect(clean_text)
            
            # Map detected languages
            language_map = {
                'en': 'english',
                'hi': 'hindi',
                'ur': 'urdu',
                'ar': 'arabic',
            }
            
            return language_map.get(detected, detected)
            
        except LangDetectException:
            return 'unknown'
        except Exception as e:
            logger.error(f"Language detection error: {e}")
            return 'unknown'
    
    def clean_text_for_analysis(self, text: str) -> str:
        """
        Clean text for sentiment analysis
        """
        if not text:
            return ""
        
        # Remove URLs
        text = self.url_extractor.remove_urls(text)
        
        # Remove emojis (but keep count)
        text = emoji.demojize(text)
        text = re.sub(r':[a-z_]+:', '', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?-]', '', text)
        
        return text
    
    def extract_features(self, message: str) -> Dict:
        """
        Extract various features from message
        """
        features = {
            'word_count': len(message.split()),
            'char_count': len(message),
            'emoji_count': len(re.findall(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]', message)),
            'contains_emoji': bool(re.search(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]', message)),
            'url_count': len(self.url_extractor.find_urls(message)),
            'contains_url': bool(self.url_extractor.has_urls(message)),
            'exclamation_count': message.count('!'),
            'question_count': message.count('?'),
            'caps_ratio': sum(1 for c in message if c.isupper()) / len(message) if message else 0,
        }
        
        return features
    
    def anonymize_participants(self, participants: List[str]) -> Dict[str, str]:
        """
        Create anonymized names for participants
        """
        anonymized = {}
        for i, participant in enumerate(sorted(set(participants))):
            if participant.lower() in ['system', 'group notification']:
                anonymized[participant] = participant
            else:
                anonymized[participant] = f"User_{i+1:02d}"
        
        return anonymized
    
    def calculate_file_hash(self, content: str) -> str:
        """
        Calculate SHA256 hash of file content
        """
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def preprocess(self, file_content: str, anonymize: bool = True) -> Dict:
        """
        Main preprocessing function
        """
        try:
            logger.info("Starting WhatsApp chat preprocessing")
            
            # Calculate file hash
            file_hash = self.calculate_file_hash(file_content)
            
            # Detect format
            format_type = self.detect_format(file_content)
            logger.info(f"Detected format: {format_type}")
            
            # Extract messages and dates
            messages, dates = self.extract_messages_and_dates(file_content, format_type)
            
            if not messages:
                raise ValueError("No messages found in the chat file")
            
            # Process each message
            processed_messages = []
            participants = set()
            
            for i, (message_text, date_str) in enumerate(zip(messages, dates)):
                try:
                    # Parse datetime
                    timestamp = self.parse_datetime(date_str, format_type)
                    if not timestamp:
                        continue
                    
                    # Extract user and message
                    username, message_content = self.extract_user_and_message(message_text)
                    
                    # Skip empty messages
                    if not message_content.strip():
                        continue
                    
                    # Determine message type
                    if self.is_system_message(message_content):
                        message_type = 'system'
                        username = 'System'
                    elif '<Media omitted>' in message_content or 'omitted' in message_content.lower():
                        message_type = 'media'
                    else:
                        message_type = 'text'
                    
                    # Add participant
                    participants.add(username)
                    
                    # Extract features
                    features = self.extract_features(message_content)
                    
                    # Detect language
                    language = self.detect_language(message_content) if message_type == 'text' else 'unknown'
                    
                    # Clean text for analysis
                    cleaned_text = self.clean_text_for_analysis(message_content)
                    
                    processed_message = {
                        'timestamp': timestamp,
                        'username': username,
                        'message_type': message_type,
                        'original_text': message_content,
                        'cleaned_text': cleaned_text,
                        'language': language,
                        'hour': timestamp.hour,
                        'day_of_week': timestamp.weekday(),
                        **features
                    }
                    
                    processed_messages.append(processed_message)
                    
                except Exception as e:
                    logger.error(f"Error processing message {i}: {e}")
                    continue
            
            # Create DataFrame
            df = pd.DataFrame(processed_messages)
            
            if df.empty:
                raise ValueError("No valid messages found after preprocessing")
            
            # Anonymize participants if requested
            participant_mapping = {}
            if anonymize:
                participant_mapping = self.anonymize_participants(list(participants))
                df['anonymized_username'] = df['username'].map(participant_mapping)
            else:
                df['anonymized_username'] = df['username']
            
            # Calculate summary statistics
            summary = {
                'total_messages': len(df),
                'total_participants': len(participants),
                'date_range_start': df['timestamp'].min(),
                'date_range_end': df['timestamp'].max(),
                'detected_languages': df['language'].value_counts().to_dict(),
                'message_types': df['message_type'].value_counts().to_dict(),
                'file_hash': file_hash,
                'format_type': format_type,
                'participant_mapping': participant_mapping,
            }
            
            logger.info(f"Preprocessing completed: {summary['total_messages']} messages, {summary['total_participants']} participants")
            
            return {
                'dataframe': df,
                'summary': summary,
                'success': True,
                'error': None
            }
            
        except Exception as e:
            logger.error(f"Preprocessing failed: {e}")
            return {
                'dataframe': None,
                'summary': None,
                'success': False,
                'error': str(e)
            }
    
    def validate_chat_file(self, file_content: str) -> Dict[str, any]:
        """
        Validate if the uploaded file is a valid WhatsApp chat export
        """
        validation_result = {
            'is_valid': False,
            'format': None,
            'issues': [],
            'warnings': []
        }
        
        try:
            # Check file size
            if len(file_content) < 100:
                validation_result['issues'].append("File too small to be a valid chat export")
                return validation_result
            
            # Check for WhatsApp patterns
            format_detected = None
            for format_name, pattern in self.patterns.items():
                if re.search(pattern, file_content[:2000]):
                    format_detected = format_name
                    break
            
            if not format_detected:
                validation_result['issues'].append("No valid WhatsApp timestamp pattern found")
                return validation_result
            
            # Check for minimum number of messages
            messages, _ = self.extract_messages_and_dates(file_content, format_detected)
            if len(messages) < 5:
                validation_result['issues'].append("Too few messages found (minimum 5 required)")
                return validation_result
            
            # Warnings for potential issues
            if len(file_content) > 50 * 1024 * 1024:  # 50MB
                validation_result['warnings'].append("Large file size may take longer to process")
            
            if len(messages) > 100000:
                validation_result['warnings'].append("Large number of messages may take longer to process")
            
            validation_result['is_valid'] = True
            validation_result['format'] = format_detected
            
        except Exception as e:
            validation_result['issues'].append(f"Validation error: {str(e)}")
        
        return validation_result