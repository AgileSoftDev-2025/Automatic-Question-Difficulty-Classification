"""
Enhanced models for Question Classification System
Includes better validation, methods, and error handling
"""

from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator, MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Sum, Count
import os
import hashlib
from pathlib import Path


def user_directory_path(instance, filename):
    """
    Generate unique file path for user uploads
    Format: classifications/user_<id>/YYYY/MM/filename
    """
    now = timezone.now()
    return f'classifications/user_{instance.user.id}/{now.year}/{now.month:02d}/{filename}'


def result_directory_path(instance, filename):
    """
    Generate unique path for result files
    Format: results/user_<id>/YYYY/MM/filename
    """
    now = timezone.now()
    return f'results/user_{instance.user.id}/{now.year}/{now.month:02d}/{filename}'


def validate_file_size(value):
    """Validate that file size is within acceptable limits (10MB)"""
    max_size = 10 * 1024 * 1024  # 10MB
    if value.size > max_size:
        raise ValidationError(f'File size cannot exceed 10MB. Current size: {value.size / (1024*1024):.1f}MB')


class Classification(models.Model):
    """
    Model for storing question classification data with enhanced features
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
        related_name='classifications',
        db_index=True
    )
    
    # File information
    file = models.FileField(
        upload_to=user_directory_path,
        validators=[
            FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx']),
            validate_file_size
        ],
        help_text='Upload PDF, DOC, or DOCX file (max 10MB)'
    )
    filename = models.CharField(max_length=255, db_index=True)
    file_size = models.IntegerField(
        default=0, 
        validators=[MinValueValidator(0)],
        help_text='File size in bytes'
    )
    file_hash = models.CharField(
        max_length=64, 
        blank=True,
        help_text='SHA256 hash of file for duplicate detection',
        db_index=True
    )
    
    # Classification results
    total_questions = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )
    q1_count = models.IntegerField(
        default=0, 
        validators=[MinValueValidator(0)],
        verbose_name='C1: Remember'
    )
    q2_count = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='C2: Understand'
    )
    q3_count = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='C3: Apply'
    )
    q4_count = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='C4: Analyze'
    )
    q5_count = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='C5: Evaluate'
    )
    q6_count = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='C6: Create'
    )
    
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
        default='pending',
        db_index=True
    )
    error_message = models.TextField(blank=True, default='')
    
    # Processing metadata
    processing_started_at = models.DateTimeField(null=True, blank=True)
    processing_completed_at = models.DateTimeField(null=True, blank=True)
    processing_time_seconds = models.IntegerField(
        null=True,
        blank=True,
        help_text='Time taken to process in seconds'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Classification'
        verbose_name_plural = 'Classifications'
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['file_hash']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(total_questions__gte=0),
                name='total_questions_non_negative'
            ),
        ]
    
    def __str__(self):
        return f"{self.filename} - {self.user.username} ({self.status})"
    
    def clean(self):
        """Validate model data"""
        super().clean()
        
        # Validate that question counts sum to total
        if self.status == 'completed':
            calculated_total = sum([
                self.q1_count, self.q2_count, self.q3_count,
                self.q4_count, self.q5_count, self.q6_count
            ])
            if calculated_total != self.total_questions:
                raise ValidationError(
                    f'Question counts ({calculated_total}) do not match total ({self.total_questions})'
                )
    
    def save(self, *args, **kwargs):
        # Set filename if not set
        if not self.filename and self.file:
            self.filename = Path(self.file.name).name
        
        # Set file size if not set
        if not self.file_size and self.file:
            self.file_size = self.file.size
        
        # Calculate file hash if not set
        if not self.file_hash and self.file:
            self.file_hash = self.calculate_file_hash()
        
        # Calculate processing time if completed
        if self.status == 'completed' and not self.processing_time_seconds:
            if self.processing_started_at and self.processing_completed_at:
                delta = self.processing_completed_at - self.processing_started_at
                self.processing_time_seconds = int(delta.total_seconds())
        
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """Override delete to remove associated files"""
        # Delete main file
        if self.file:
            try:
                if os.path.isfile(self.file.path):
                    os.remove(self.file.path)
            except Exception as e:
                print(f"Error deleting file {self.file.path}: {e}")
        
        # Delete result file
        if self.result_file:
            try:
                if os.path.isfile(self.result_file.path):
                    os.remove(self.result_file.path)
            except Exception as e:
                print(f"Error deleting result file {self.result_file.path}: {e}")
        
        super().delete(*args, **kwargs)
    
    def calculate_file_hash(self):
        """Calculate SHA256 hash of the file"""
        if not self.file:
            return ''
        
        try:
            self.file.seek(0)
            file_hash = hashlib.sha256()
            
            # Read file in chunks
            for chunk in self.file.chunks():
                file_hash.update(chunk)
            
            self.file.seek(0)
            return file_hash.hexdigest()
        except Exception as e:
            print(f"Error calculating file hash: {e}")
            return ''
    
    def start_processing(self):
        """Mark classification as processing"""
        self.status = 'processing'
        self.processing_started_at = timezone.now()
        self.error_message = ''
        self.save(update_fields=['status', 'processing_started_at', 'error_message'])
    
    def mark_completed(self):
        """Mark classification as completed"""
        self.status = 'completed'
        self.processing_completed_at = timezone.now()
        if self.processing_started_at:
            delta = self.processing_completed_at - self.processing_started_at
            self.processing_time_seconds = int(delta.total_seconds())
        self.save(update_fields=['status', 'processing_completed_at', 'processing_time_seconds'])
    
    def mark_failed(self, error_message):
        """Mark classification as failed"""
        self.status = 'failed'
        self.error_message = error_message
        self.processing_completed_at = timezone.now()
        self.save(update_fields=['status', 'error_message', 'processing_completed_at'])
    
    def recalculate_counts(self):
        """Recalculate question counts from related questions"""
        counts = self.questions.values('category').annotate(count=Count('id'))
        
        # Reset counts
        self.q1_count = 0
        self.q2_count = 0
        self.q3_count = 0
        self.q4_count = 0
        self.q5_count = 0
        self.q6_count = 0
        
        # Update counts from aggregation
        for item in counts:
            category = item['category']
            count = item['count']
            if category == 'C1':
                self.q1_count = count
            elif category == 'C2':
                self.q2_count = count
            elif category == 'C3':
                self.q3_count = count
            elif category == 'C4':
                self.q4_count = count
            elif category == 'C5':
                self.q5_count = count
            elif category == 'C6':
                self.q6_count = count
        
        self.total_questions = self.questions.count()
        self.save(update_fields=[
            'q1_count', 'q2_count', 'q3_count', 'q4_count', 'q5_count', 'q6_count', 'total_questions'
        ])
    
    @property
    def formatted_created_at(self):
        """Return formatted date string"""
        return self.created_at.strftime('%d/%m/%Y')
    
    @property
    def formatted_created_at_time(self):
        """Return formatted datetime string"""
        return self.created_at.strftime('%d/%m/%Y %H:%M')
    
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
        status_map = {
            'completed': 100,
            'processing': 50,
            'pending': 25,
            'failed': 0
        }
        return status_map.get(self.status, 0)
    
    @property
    def has_results(self):
        """Check if classification has been processed"""
        return self.status == 'completed' and self.total_questions > 0
    
    @property
    def distribution_percentages(self):
        """Get percentage distribution of questions by category"""
        if self.total_questions == 0:
            return {f'C{i}': 0 for i in range(1, 7)}
        
        return {
            'C1': round((self.q1_count / self.total_questions) * 100, 1),
            'C2': round((self.q2_count / self.total_questions) * 100, 1),
            'C3': round((self.q3_count / self.total_questions) * 100, 1),
            'C4': round((self.q4_count / self.total_questions) * 100, 1),
            'C5': round((self.q5_count / self.total_questions) * 100, 1),
            'C6': round((self.q6_count / self.total_questions) * 100, 1),
        }
    
    @property
    def formatted_processing_time(self):
        """Return human-readable processing time"""
        if not self.processing_time_seconds:
            return 'N/A'
        
        seconds = self.processing_time_seconds
        if seconds < 60:
            return f"{seconds} seconds"
        elif seconds < 3600:
            minutes = seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''}"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}h {minutes}m"


class Question(models.Model):
    """
    Model for storing individual question details with enhanced validation
    """
    CATEGORY_CHOICES = [
        ('C1', 'C1: Remember'),
        ('C2', 'C2: Understand'),
        ('C3', 'C3: Apply'),
        ('C4', 'C4: Analyze'),
        ('C5', 'C5: Evaluate'),
        ('C6', 'C6: Create'),
    ]
    
    CATEGORY_DESCRIPTIONS = {
        'C1': 'Recall facts and basic concepts',
        'C2': 'Explain ideas or concepts',
        'C3': 'Use information in new situations',
        'C4': 'Draw connections among ideas',
        'C5': 'Justify a decision or course of action',
        'C6': 'Produce new or original work',
    }
    
    classification = models.ForeignKey(
        Classification,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    
    question_number = models.IntegerField(
        validators=[MinValueValidator(1)]
    )
    question_text = models.TextField()
    category = models.CharField(
        max_length=2, 
        choices=CATEGORY_CHOICES,
        db_index=True
    )
    confidence_score = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text='ML model confidence score (0-1)'
    )
    
    # Optional: Multiple choice options
    choice_a = models.TextField(blank=True, default='')
    choice_b = models.TextField(blank=True, default='')
    choice_c = models.TextField(blank=True, default='')
    choice_d = models.TextField(blank=True, default='')
    choice_e = models.TextField(blank=True, default='')
    correct_answer = models.CharField(
        max_length=1,
        blank=True,
        default='',
        choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('E', 'E')]
    )
    
    # Metadata
    is_manually_classified = models.BooleanField(
        default=False,
        help_text='Whether this question was manually reclassified'
    )
    previous_category = models.CharField(
        max_length=2,
        blank=True,
        help_text='Previous category before manual reclassification'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['question_number']
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'
        unique_together = [['classification', 'question_number']]
        indexes = [
            models.Index(fields=['classification', 'question_number']),
            models.Index(fields=['category']),
            models.Index(fields=['confidence_score']),
        ]
    
    def __str__(self):
        return f"Q{self.question_number} - {self.category} ({self.classification.filename})"
    
    def clean(self):
        """Validate question data"""
        super().clean()
        
        if not self.question_text.strip():
            raise ValidationError('Question text cannot be empty')
        
        if len(self.question_text) > 5000:
            raise ValidationError('Question text is too long (max 5000 characters)')
    
    def save(self, *args, **kwargs):
        # Track category changes for manual classification
        if self.pk:
            try:
                old_instance = Question.objects.get(pk=self.pk)
                if old_instance.category != self.category:
                    self.previous_category = old_instance.category
                    self.is_manually_classified = True
            except Question.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)
        
        # Update parent classification counts
        if self.classification:
            self.classification.recalculate_counts()
    
    @property
    def category_name(self):
        """Get full category name"""
        category_names = {
            'C1': 'Remember',
            'C2': 'Understand',
            'C3': 'Apply',
            'C4': 'Analyze',
            'C5': 'Evaluate',
            'C6': 'Create',
        }
        return category_names.get(self.category, 'Unknown')
    
    @property
    def category_description(self):
        """Get category description"""
        return self.CATEGORY_DESCRIPTIONS.get(self.category, '')
    
    @property
    def formatted_confidence(self):
        """Return formatted confidence score as percentage"""
        return f"{self.confidence_score * 100:.1f}%"
    
    @property
    def has_choices(self):
        """Check if question has multiple choice options"""
        return any([self.choice_a, self.choice_b, self.choice_c, self.choice_d, self.choice_e])
    
    @property
    def choices_list(self):
        """Return list of non-empty choices"""
        choices = []
        for label, text in [
            ('A', self.choice_a),
            ('B', self.choice_b),
            ('C', self.choice_c),
            ('D', self.choice_d),
            ('E', self.choice_e)
        ]:
            if text:
                choices.append({'label': label, 'text': text})
        return choices


# Signal handlers
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver

@receiver(post_delete, sender=Classification)
def classification_delete_files(sender, instance, **kwargs):
    """Delete files when Classification instance is deleted"""
    if instance.file:
        try:
            if os.path.isfile(instance.file.path):
                os.remove(instance.file.path)
        except Exception as e:
            print(f"Error deleting file: {e}")
    
    if instance.result_file:
        try:
            if os.path.isfile(instance.result_file.path):
                os.remove(instance.result_file.path)
        except Exception as e:
            print(f"Error deleting result file: {e}")


@receiver(pre_save, sender=Question)
def question_update_classification(sender, instance, **kwargs):
    """Update classification counts when question is updated"""
    if instance.pk:
        try:
            old_question = Question.objects.get(pk=instance.pk)
            if old_question.category != instance.category:
                # Category changed, will trigger recalculation in save method
                pass
        except Question.DoesNotExist:
            pass