# ===================================
# FILE: apps/klasifikasi/models.py
# ===================================

from django.db import models
from django.conf import settings

class Classification(models.Model):
    """
    Model untuk menyimpan data klasifikasi soal berdasarkan Bloom's Taxonomy
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='classifications',
        verbose_name='User'
    )
    
    # Informasi File
    filename = models.CharField(max_length=255, verbose_name='File Name')
    file = models.FileField(
        upload_to='uploads/questions/',
        verbose_name='Question File'
    )
    result_file = models.FileField(
        upload_to='uploads/results/',
        null=True,
        blank=True,
        verbose_name='Result File'
    )
    
    # Jumlah soal per kategori Bloom's Taxonomy
    total_questions = models.IntegerField(default=0, verbose_name='Total Questions')
    q1_count = models.IntegerField(default=0, verbose_name='C1 - Remember')
    q2_count = models.IntegerField(default=0, verbose_name='C2 - Understand')
    q3_count = models.IntegerField(default=0, verbose_name='C3 - Apply')
    q4_count = models.IntegerField(default=0, verbose_name='C4 - Analyze')
    q5_count = models.IntegerField(default=0, verbose_name='C5 - Evaluate')
    q6_count = models.IntegerField(default=0, verbose_name='C6 - Create')
    
    # Status klasifikasi
    STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='processing',
        verbose_name='Status'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    
    # Notes atau keterangan tambahan (opsional)
    notes = models.TextField(blank=True, null=True, verbose_name='Notes')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Classification'
        verbose_name_plural = 'Classifications'
        db_table = 'classification'
    
    def __str__(self):
        return f"{self.filename} - {self.user.username} ({self.created_at.strftime('%d/%m/%Y')})"
    
    def get_distribution_percentage(self):
        """
        Menghitung persentase distribusi soal per kategori
        """
        if self.total_questions == 0:
            return {
                'q1': 0, 'q2': 0, 'q3': 0,
                'q4': 0, 'q5': 0, 'q6': 0
            }
        
        return {
            'q1': round((self.q1_count / self.total_questions) * 100, 2),
            'q2': round((self.q2_count / self.total_questions) * 100, 2),
            'q3': round((self.q3_count / self.total_questions) * 100, 2),
            'q4': round((self.q4_count / self.total_questions) * 100, 2),
            'q5': round((self.q5_count / self.total_questions) * 100, 2),
            'q6': round((self.q6_count / self.total_questions) * 100, 2),
        }
    
    def is_completed(self):
        """
        Cek apakah klasifikasi sudah selesai
        """
        return self.status == 'completed'
