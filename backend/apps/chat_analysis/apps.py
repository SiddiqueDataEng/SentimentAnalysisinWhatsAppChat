"""
Chat Analysis app configuration
"""
from django.apps import AppConfig


class ChatAnalysisConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.chat_analysis'
    verbose_name = 'Chat Analysis'
    
    def ready(self):
        """Import signal handlers"""
        try:
            import apps.chat_analysis.signals
        except ImportError:
            pass