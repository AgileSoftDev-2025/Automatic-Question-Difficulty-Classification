"""
Enhanced models for Question Classification System
Includes comprehensive validation, methods, properties, and error handling
"""

from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator, MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Sum, Count, Q, Avg
from django.urls import reverse
import os
import hashlib
from pathlib import Path
from datetime import timedelta


def user_directory_path(instance, filename):
    """
    Generate unique file path for user uploads
    Format: classifications/user_<id>/YYYY/MM/filename
    """
    now = timezone.now()
    # Sanitize filename
    filename = Path(filename).name
    return f'classifications/user_{instance.user.id}/{now.year}/{now.month:02d}/{filename}'


def result_directory_path(instance, filename):
    """
    Generate unique path for result files
    Format: results/user_<id>/YYYY/MM/filename
    """
    now = timezone.now()
    filename = Path(filename).name
    return f'results/user_{instance.user.id}/{now.year}/{now.month:02d}/{filename}'


def validate_file_size(value):
    """Validate that file size is within acceptable limits (10MB)"""
    max_size = 10 * 1024 * 1024  # 10MB
    if value.size > max_size:
        raise ValidationError(
            f'File size cannot exceed 10MB. Current size: {value.size / (1024*1024):.1f}MB'
        )


def validate_file_extension(value):
    """Additional validation for file extensions"""
    valid_extensions = ['.pdf', '.doc', '.docx']
    ext = os.path.splitext(value.name)[1].lower()
    if ext not in valid_extensions:
        raise ValidationError(
            f'Unsupported file extension "{ext}". Allowed extensions: {", ".join(valid_extensions)}'
        )


class ClassificationManager(models.Manager):
    """Custom manager for Classification model"""
    
    def get_queryset(self):
        """Override default queryset"""
        return super().get_queryset().select_related('user')
    
    def completed(self):
        """Get completed classifications"""
        return self.filter(status='completed')
    
    def pending(self):
        """Get pending classifications"""
        return self.filter(status='pending')
    
    def processing(self):
        """Get processing classifications"""
        return self.filter(status='processing')
    
    def failed(self):
        """Get failed classifications"""
        return self.filter(status='failed')
    
    def for_user(self, user):
        """Get classifications for specific user"""
        return self.filter(user=user)
    
    def recent(self, days=30):
        """Get recent classifications within specified days"""
        date_threshold = timezone.now() - timedelta(days=days)
        return self.filter(created_at__gte=date_threshold)


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
        db_index=True,
        help_text='User who owns this classification'
    )
    
    # File information
    file = models.FileField(
        upload_to=user_directory_path,
        validators=[
            FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx']),
            validate_file_size,
            validate_file_extension
        ],
        help_text='Upload PDF, DOC, or DOCX file (max 10MB)'
    )
    filename = models.CharField(
        max_length=255, 
        db_index=True,
        help_text='Original filename'
    )
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
        validators=[MinValueValidator(0)],
        help_text='Total number of questions classified'
    )
    q1_count = models.IntegerField(
        default=0, 
        validators=[MinValueValidator(0)],
        verbose_name='C1: Remember',
        help_text='Number of C1 level questions'
    )
    q2_count = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='C2: Understand',
        help_text='Number of C2 level questions'
    )
    q3_count = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='C3: Apply',
        help_text='Number of C3 level questions'
    )
    q4_count = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='C4: Analyze',
        help_text='Number of C4 level questions'
    )
    q5_count = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='C5: Evaluate',
        help_text='Number of C5 level questions'
    )
    q6_count = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='C6: Create',
        help_text='Number of C6 level questions'
    )
    
    # Result file
    result_file = models.FileField(
        upload_to=result_directory_path,
        null=True,
        blank=True,
        help_text='Generated report file (PDF)'
    )
    
    # Status and metadata
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending',
        db_index=True,
        help_text='Current processing status'
    )
    error_message = models.TextField(
        blank=True, 
        default='',
        help_text='Error message if processing failed'
    )
    
    # Processing metadata
    processing_started_at = models.DateTimeField(
        null=True, 
        blank=True,
        help_text='When processing started'
    )
    processing_completed_at = models.DateTimeField(
        null=True, 
        blank=True,
        help_text='When processing completed'
    )
    processing_time_seconds = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text='Time taken to process in seconds'
    )
    
    # Task tracking (for Celery)
    task_id = models.CharField(
        max_length=255,
        blank=True,
        default='',
        help_text='Celery task ID for tracking'
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True, 
        db_index=True,
        help_text='When this classification was created'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='When this classification was last updated'
    )
    
    # Custom manager
    objects = ClassificationManager()
    
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
        return f"{self.filename} - {self.user.username} ({self.get_status_display()})"
    
    def clean(self):
        """Validate model data"""
        super().clean()
        
        # Validate that question counts sum to total (only for completed)
        if self.status == 'completed':
            calculated_total = sum([
                self.q1_count, self.q2_count, self.q3_count,
                self.q4_count, self.q5_count, self.q6_count
            ])
            if calculated_total != self.total_questions:
                raise ValidationError(
                    f'Question counts ({calculated_total}) do not match total ({self.total_questions})'
                )
        
        # Validate file exists
        if self.file and not os.path.exists(self.file.path):
            raise ValidationError('File does not exist on disk')
    
    def save(self, *args, **kwargs):
        """Override save to set defaults and validate"""
        # Set filename if not set
        if not self.filename and self.file:
            self.filename = Path(self.file.name).name
        
        # Set file size if not set
        if not self.file_size and self.file:
            try:
                self.file_size = self.file.size
            except Exception:
                self.file_size = 0
        
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
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Error deleting file {self.file.path}: {e}")
        
        # Delete result file
        if self.result_file:
            try:
                if os.path.isfile(self.result_file.path):
                    os.remove(self.result_file.path)
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Error deleting result file {self.result_file.path}: {e}")
        
        super().delete(*args, **kwargs)
    
    def calculate_file_hash(self):
        """Calculate SHA256 hash of the file"""
        if not self.file:
            return ''
        
        try:
            self.file.seek(0)
            file_hash = hashlib.sha256()
            
            # Read file in chunks to handle large files
            for chunk in self.file.chunks(chunk_size=8192):
                file_hash.update(chunk)
            
            self.file.seek(0)
            return file_hash.hexdigest()
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error calculating file hash: {e}")
            return ''
    
    def start_processing(self):
        """Mark classification as processing"""
        self.status = 'processing'
        self.processing_started_at = timezone.now()
        self.error_message = ''
        self.save(update_fields=['status', 'processing_started_at', 'error_message', 'updated_at'])
    
    def mark_completed(self):
        """Mark classification as completed"""
        self.status = 'completed'
        self.processing_completed_at = timezone.now()
        if self.processing_started_at:
            delta = self.processing_completed_at - self.processing_started_at
            self.processing_time_seconds = int(delta.total_seconds())
        self.save(update_fields=['status', 'processing_completed_at', 'processing_time_seconds', 'updated_at'])
    
    def mark_failed(self, error_message):
        """Mark classification as failed with error message"""
        self.status = 'failed'
        self.error_message = error_message
        self.processing_completed_at = timezone.now()
        self.save(update_fields=['status', 'error_message', 'processing_completed_at', 'updated_at'])
    
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
            'q1_count', 'q2_count', 'q3_count', 'q4_count', 'q5_count', 'q6_count', 
            'total_questions', 'updated_at'
        ])
    
    def get_absolute_url(self):
        """Get URL for this classification"""
        return reverse('klasifikasi:hasil_klasifikasi', kwargs={'pk': self.pk})
    
    # Properties
    
    @property
    def formatted_created_at(self):
        """Return formatted date string (DD/MM/YYYY)"""
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
        """Check if classification has been processed successfully"""
        return self.status == 'completed' and self.total_questions > 0
    
    @property
    def distribution_percentages(self):
        """Get percentage distribution of questions by category"""
        if self.total_questions == 0:
            return {f'C{i}': 0.0 for i in range(1, 7)}
        
        return {
            'C1': round((self.q1_count / self.total_questions) * 100, 1),
            'C2': round((self.q2_count / self.total_questions) * 100, 1),
            'C3': round((self.q3_count / self.total_questions) * 100, 1),
            'C4': round((self.q4_count / self.total_questions) * 100, 1),
            'C5': round((self.q5_count / self.total_questions) * 100, 1),
            'C6': round((self.q6_count / self.total_questions) * 100, 1),
        }
    
    @property
    def distribution_counts(self):
        """Get count distribution as dictionary"""
        return {
            'C1': self.q1_count,
            'C2': self.q2_count,
            'C3': self.q3_count,
            'C4': self.q4_count,
            'C5': self.q5_count,
            'C6': self.q6_count,
        }
    
    @property
    def formatted_processing_time(self):
        """Return human-readable processing time"""
        if not self.processing_time_seconds:
            return 'N/A'
        
        seconds = self.processing_time_seconds
        if seconds < 60:
            return f"{seconds} second{'s' if seconds != 1 else ''}"
        elif seconds < 3600:
            minutes = seconds // 60
            remaining_seconds = seconds % 60
            if remaining_seconds > 0:
                return f"{minutes}m {remaining_seconds}s"
            return f"{minutes} minute{'s' if minutes != 1 else ''}"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}h {minutes}m"
    
    @property
    def avg_confidence(self):
        """Get average confidence score across all questions"""
        avg = self.questions.aggregate(Avg('confidence_score'))['confidence_score__avg']
        return round(avg * 100, 1) if avg else 0
    
    @property
    def manually_classified_count(self):
        """Get count of manually reclassified questions"""
        return self.questions.filter(is_manually_classified=True).count()
    
    @property
    def is_processing(self):
        """Check if classification is currently processing"""
        return self.status == 'processing'
    
    @property
    def is_completed(self):
        """Check if classification is completed"""
        return self.status == 'completed'
    
    @property
    def is_failed(self):
        """Check if classification failed"""
        return self.status == 'failed'
    
    @property
    def can_be_deleted(self):
        """Check if classification can be safely deleted"""
        return self.status in ['completed', 'failed', 'pending']
    
    @property
    def dominant_category(self):
        """Get the category with the most questions"""
        counts = self.distribution_counts
        if not any(counts.values()):
            return None
        return max(counts, key=counts.get)


class QuestionManager(models.Manager):
    """Custom manager for Question model"""
    
    def get_queryset(self):
        """Override default queryset"""
        return super().get_queryset().select_related('classification')
    
    def by_category(self, category):
        """Get questions by category"""
        return self.filter(category=category)
    
    def manually_classified(self):
        """Get manually classified questions"""
        return self.filter(is_manually_classified=True)
    
    def high_confidence(self, threshold=0.8):
        """Get questions with high confidence score"""
        return self.filter(confidence_score__gte=threshold)
    
    def low_confidence(self, threshold=0.6):
        """Get questions with low confidence score"""
        return self.filter(confidence_score__lt=threshold)


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
    
    CATEGORY_NAMES = {
        'C1': 'Remember',
        'C2': 'Understand',
        'C3': 'Apply',
        'C4': 'Analyze',
        'C5': 'Evaluate',
        'C6': 'Create',
    }
    
    classification = models.ForeignKey(
        Classification,
        on_delete=models.CASCADE,
        related_name='questions',
        help_text='Classification this question belongs to'
    )
    
    question_number = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text='Question number in the original document'
    )
    question_text = models.TextField(
        help_text='The actual question text'
    )
    category = models.CharField(
        max_length=2, 
        choices=CATEGORY_CHOICES,
        db_index=True,
        help_text='Bloom\'s Taxonomy category'
    )
    confidence_score = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text='ML model confidence score (0-1)'
    )
    
    # Optional: Multiple choice options
    choice_a = models.TextField(blank=True, default='', help_text='Choice A')
    choice_b = models.TextField(blank=True, default='', help_text='Choice B')
    choice_c = models.TextField(blank=True, default='', help_text='Choice C')
    choice_d = models.TextField(blank=True, default='', help_text='Choice D')
    choice_e = models.TextField(blank=True, default='', help_text='Choice E')
    correct_answer = models.CharField(
        max_length=1,
        blank=True,
        default='',
        choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('E', 'E')],
        help_text='Correct answer choice'
    )
    
    # Metadata
    is_manually_classified = models.BooleanField(
        default=False,
        help_text='Whether this question was manually reclassified',
        db_index=True
    )
    previous_category = models.CharField(
        max_length=2,
        blank=True,
        help_text='Previous category before manual reclassification'
    )
    notes = models.TextField(
        blank=True,
        default='',
        help_text='Additional notes about this question'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Custom manager
    objects = QuestionManager()
    
    class Meta:
        ordering = ['question_number']
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'
        unique_together = [['classification', 'question_number']]
        indexes = [
            models.Index(fields=['classification', 'question_number']),
            models.Index(fields=['category']),
            models.Index(fields=['confidence_score']),
            models.Index(fields=['is_manually_classified']),
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
        
        # Validate confidence score
        if not 0 <= self.confidence_score <= 1:
            raise ValidationError('Confidence score must be between 0 and 1')
    
    def save(self, *args, **kwargs):
        """Override save to track changes"""
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
        # Note: This can be expensive, consider using signals or batch updates
        if self.classification:
            self.classification.recalculate_counts()
    
    @property
    def category_name(self):
        """Get full category name"""
        return self.CATEGORY_NAMES.get(self.category, 'Unknown')
    
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
                choices.append({
                    'label': label, 
                    'text': text,
                    'is_correct': label == self.correct_answer
                })
        return choices
    
    @property
    def is_high_confidence(self):
        """Check if question has high confidence (>= 80%)"""
        return self.confidence_score >= 0.8
    
    @property
    def is_low_confidence(self):
        """Check if question has low confidence (< 60%)"""
        return self.confidence_score < 0.6
    
    @property
    def confidence_label(self):
        """Get confidence label (High/Medium/Low)"""
        if self.confidence_score >= 0.8:
            return 'High'
        elif self.confidence_score >= 0.6:
            return 'Medium'
        else:
            return 'Low'


# Signal handlers
from django.db.models.signals import post_delete, pre_save, post_save
from django.dispatch import receiver

@receiver(post_delete, sender=Classification)
def classification_delete_files(sender, instance, **kwargs):
    """Delete files when Classification instance is deleted"""
    if instance.file:
        try:
            if os.path.isfile(instance.file.path):
                os.remove(instance.file.path)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Error deleting file: {e}")
    
    if instance.result_file:
        try:
            if os.path.isfile(instance.result_file.path):
                os.remove(instance.result_file.path)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Error deleting result file: {e}")


@receiver(pre_save, sender=Question)
def question_track_changes(sender, instance, **kwargs):
    """Track question category changes"""
    if instance.pk:
        try:
            old_question = Question.objects.get(pk=instance.pk)
            if old_question.category != instance.category:
                instance.previous_category = old_question.category
                instance.is_manually_classified = True
        except Question.DoesNotExist:
            pass


@receiver(post_save, sender=Question)
def question_update_classification(sender, instance, created, **kwargs):
    """Update classification counts when question is saved"""
    # Note: This is called in Question.save() as well
    # Consider removing one to avoid double counting
    pass