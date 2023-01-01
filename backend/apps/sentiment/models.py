"""
Sentiment analysis models
"""
from django.db import models
from django.utils.translation import gettext_lazy as _


class SentimentModel(models.Model):
    """
    Model to store sentiment analysis model information
    """
    name = models.CharField(max_length=100, unique=True)
    version = models.CharField(max_length=50)
    model_type = models.CharField(max_length=50)
    supported_languages = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)
    accuracy_score = models.FloatField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'sentiment_models'
        verbose_name = _('Sentiment Model')
        verbose_name_plural = _('Sentiment Models')
    
    def __str__(self):
        return f"{self.name} v{self.version}"


class ModelPerformance(models.Model):
    """
    Model to track sentiment model performance metrics
    """
    model = models.ForeignKey(SentimentModel, on_delete=models.CASCADE, related_name='performance_metrics')
    
    # Performance metrics
    accuracy = models.FloatField()
    precision = models.FloatField()
    recall = models.FloatField()
    f1_score = models.FloatField()
    
    # Test data info
    test_dataset_size = models.PositiveIntegerField()
    test_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'model_performance'
        verbose_name = _('Model Performance')
        verbose_name_plural = _('Model Performance')
        ordering = ['-test_date']
    
    def __str__(self):
        return f"{self.model.name} - Accuracy: {self.accuracy:.3f}"