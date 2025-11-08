# apps/soal/models.py

from django.db import models
from django.conf import settings
from django.utils import timezone

class ClassificationHistory(models.Model):
    """
    Store user's file upload and classification history
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='classification_history'
    )
    filename = models.CharField(max_length=255, help_text="Original filename")
    file_path = models.CharField(max_length=500, help_text="Stored file path",null=True, blank=True)
    file_url = models.URLField(max_length=500, blank=True, null=True)
    file_size = models.IntegerField(default=0, help_text="File size in bytes")
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    # Classification results (can be JSON field)
    classification_results = models.JSONField(blank=True, null=True)
    total_questions = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Classification History'
        verbose_name_plural = 'Classification Histories'
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.filename} ({self.status})"
    
    def mark_as_processing(self):
        """Mark classification as processing"""
        self.status = 'processing'
        self.save(update_fields=['status', 'updated_at'])
    
    def mark_as_completed(self, results=None, total_questions=0):
        """Mark classification as completed"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        if results:
            self.classification_results = results
        self.total_questions = total_questions
        self.save(update_fields=['status', 'completed_at', 'classification_results', 'total_questions', 'updated_at'])
    
    def mark_as_failed(self):
        """Mark classification as failed"""
        self.status = 'failed'
        self.save(update_fields=['status', 'updated_at'])