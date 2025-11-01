from django.db import models
from django.conf import settings

class ClassificationHistory(models.Model):
    """Stores a record of a file classification attempt."""
    STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='classification_history')
    filename = models.CharField(max_length=255)
    file_url = models.CharField(max_length=512)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.filename} by {self.user.username} at {self.created_at.strftime("%Y-%m-%d %H:%M")}'
