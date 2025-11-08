# ===================================
# FILE: models.py (untuk app klasifikasi)
# Path: Automatic-Question-Difficulty-Classification/apps/klasifikasi/models.py
# ===================================

from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.utils import timezone
import os


def user_directory_path(instance, filename):
    """
    File akan di-upload ke MEDIA_ROOT/user_<id>/<filename>
    """
    return f'classifications/user_{instance.user.id}/{filename}'


def result_directory_path(instance, filename):
    """
    File hasil akan di-upload ke MEDIA_ROOT/results/user_<id>/<filename>
    """
    return f'results/user_{instance.user.id}/{filename}'


class Classification(models.Model):
    """
    Model untuk menyimpan data klasifikasi soal
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    # User information
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='classifications'
    )
    
    # File information
    file = models.FileField(
        upload_to=user_directory_path,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx'])],
        help_text='Upload PDF, DOC, or DOCX file'
    )
    filename = models.CharField(max_length=255)
    file_size = models.IntegerField(default=0, help_text='File size in bytes')
    
    # Classification results
    total_questions = models.IntegerField(default=0)
    q1_count = models.IntegerField(default=0, verbose_name='C1: Remember')
    q2_count = models.IntegerField(default=0, verbose_name='C2: Understand')
    q3_count = models.IntegerField(default=0, verbose_name='C3: Apply')
    q4_count = models.IntegerField(default=0, verbose_name='C4: Analyze')
    q5_count = models.IntegerField(default=0, verbose_name='C5: Evaluate')
    q6_count = models.IntegerField(default=0, verbose_name='C6: Create')
    
    # Result file
    result_file = models.FileField(
        upload_to=result_directory_path,
        null=True,
        blank=True,
        help_text='Generated report file'
    )
    
    # Status and metadata
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending'
    )
    error_message = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Classification'
        verbose_name_plural = 'Classifications'
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.filename} - {self.user.username} ({self.created_at.strftime('%Y-%m-%d')})"
    
    def save(self, *args, **kwargs):
        # Set filename if not already set
        if not self.filename and self.file:
            self.filename = os.path.basename(self.file.name)
        
        # Set file size if not already set
        if not self.file_size and self.file:
            self.file_size = self.file.size
        
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """
        Override delete to also remove files
        """
        if self.file and os.path.isfile(self.file.path):
            os.remove(self.file.path)
        
        if self.result_file and os.path.isfile(self.result_file.path):
            os.remove(self.result_file.path)
        
        super().delete(*args, **kwargs)
    
    @property
    def formatted_created_at(self):
        """Return formatted date string"""
        return self.created_at.strftime('%d/%m/%Y')
    
    @property
    def formatted_file_size(self):
        """Return human-readable file size"""
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    @property
    def completion_percentage(self):
        """Calculate completion percentage based on status"""
        if self.status == 'completed':
            return 100
        elif self.status == 'processing':
            return 50
        elif self.status == 'pending':
            return 25
        else:
            return 0
    
    @property
    def has_results(self):
        """Check if classification has been processed"""
        return self.status == 'completed' and self.total_questions > 0


class Question(models.Model):
    """
    Model untuk menyimpan detail setiap pertanyaan yang diklasifikasi
    """
    CATEGORY_CHOICES = [
        ('C1', 'C1: Remember'),
        ('C2', 'C2: Understand'),
        ('C3', 'C3: Apply'),
        ('C4', 'C4: Analyze'),
        ('C5', 'C5: Evaluate'),
        ('C6', 'C6: Create'),
    ]
    
    classification = models.ForeignKey(
        Classification,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    
    question_number = models.IntegerField()
    question_text = models.TextField()
    category = models.CharField(max_length=2, choices=CATEGORY_CHOICES)
    confidence_score = models.FloatField(
        default=0.0,
        help_text='ML model confidence score (0-1)'
    )
    
    # Optional: Store answer choices for multiple choice questions
    choice_a = models.TextField(blank=True, null=True)
    choice_b = models.TextField(blank=True, null=True)
    choice_c = models.TextField(blank=True, null=True)
    choice_d = models.TextField(blank=True, null=True)
    choice_e = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['question_number']
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'
        indexes = [
            models.Index(fields=['classification', 'question_number']),
            models.Index(fields=['category']),
        ]
    
    def __str__(self):
        return f"Q{self.question_number} - {self.category} ({self.classification.filename})"
    
    @property
    def category_name(self):
        """Get full category name"""
        category_map = {
            'C1': 'Remember',
            'C2': 'Understand',
            'C3': 'Apply',
            'C4': 'Analyze',
            'C5': 'Evaluate',
            'C6': 'Create',
        }
        return category_map.get(self.category, 'Unknown')
    
    @property
    def formatted_confidence(self):
        """Return formatted confidence score as percentage"""
        return f"{self.confidence_score * 100:.1f}%"


# ===================================
# SIGNAL HANDLERS (Optional)
# ===================================

from django.db.models.signals import post_delete
from django.dispatch import receiver

@receiver(post_delete, sender=Classification)
def classification_delete_files(sender, instance, **kwargs):
    """
    Delete files when Classification instance is deleted
    """
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)
    
    if instance.result_file:
        if os.path.isfile(instance.result_file.path):
            os.remove(instance.result_file.path)