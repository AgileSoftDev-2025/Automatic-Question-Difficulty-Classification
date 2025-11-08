# ===================================
# FILE: admin.py (untuk app klasifikasi)
# Path: Automatic-Question-Difficulty-Classification/apps/klasifikasi/admin.py
# ===================================

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
# from .models import Classification, Question


# Uncomment when models are ready
"""
@admin.register(Classification)
class ClassificationAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'filename_link',
        'user_link',
        'total_questions',
        'status_badge',
        'category_distribution',
        'formatted_file_size',
        'formatted_created_at',
    ]
    
    list_filter = [
        'status',
        'created_at',
        'processed_at',
    ]
    
    search_fields = [
        'filename',
        'user__username',
        'user__email',
    ]
    
    readonly_fields = [
        'created_at',
        'updated_at',
        'processed_at',
        'file_size',
        'detailed_info',
    ]
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('File Information', {
            'fields': ('file', 'filename', 'file_size')
        }),
        ('Classification Results', {
            'fields': (
                'total_questions',
                'q1_count',
                'q2_count',
                'q3_count',
                'q4_count',
                'q5_count',
                'q6_count',
            )
        }),
        ('Result File', {
            'fields': ('result_file',)
        }),
        ('Status', {
            'fields': ('status', 'error_message')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'processed_at'),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': ('detailed_info',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_completed', 'mark_as_failed', 'reprocess_classification']
    
    def filename_link(self, obj):
        url = reverse('admin:klasifikasi_classification_change', args=[obj.id])
        return format_html('<a href="{}">{}</a>', url, obj.filename)
    filename_link.short_description = 'Filename'
    
    def user_link(self, obj):
        url = reverse('admin:auth_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = 'User'
    
    def status_badge(self, obj):
        color_map = {
            'pending': 'orange',
            'processing': 'blue',
            'completed': 'green',
            'failed': 'red',
        }
        color = color_map.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def category_distribution(self, obj):
        if obj.total_questions == 0:
            return "No questions"
        
        categories = [
            ('C1', obj.q1_count, '#10b981'),
            ('C2', obj.q2_count, '#3b82f6'),
            ('C3', obj.q3_count, '#eab308'),
            ('C4', obj.q4_count, '#f97316'),
            ('C5', obj.q5_count, '#a855f7'),
            ('C6', obj.q6_count, '#ef4444'),
        ]
        
        html = '<div style="display: flex; gap: 5px;">'
        for name, count, color in categories:
            if count > 0:
                html += f'<span style="background-color: {color}; color: white; ' \
                       f'padding: 2px 6px; border-radius: 3px; font-size: 11px;">' \
                       f'{name}: {count}</span>'
        html += '</div>'
        return mark_safe(html)
    category_distribution.short_description = 'Categories'
    
    def detailed_info(self, obj):
        if not obj.id:
            return "Save the classification first to see detailed info."
        
        html = f'''
        <div style="padding: 10px; background: #f9fafb; border-radius: 5px;">
            <h3 style="margin-top: 0;">Classification Details</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="padding: 5px; font-weight: bold;">ID:</td>
                    <td style="padding: 5px;">{obj.id}</td>
                </tr>
                <tr>
                    <td style="padding: 5px; font-weight: bold;">User:</td>
                    <td style="padding: 5px;">{obj.user.get_full_name() or obj.user.username}</td>
                </tr>
                <tr>
                    <td style="padding: 5px; font-weight: bold;">Email:</td>
                    <td style="padding: 5px;">{obj.user.email}</td>
                </tr>
                <tr>
                    <td style="padding: 5px; font-weight: bold;">File Size:</td>
                    <td style="padding: 5px;">{obj.formatted_file_size}</td>
                </tr>
                <tr>
                    <td style="padding: 5px; font-weight: bold;">Total Questions:</td>
                    <td style="padding: 5px;">{obj.total_questions}</td>
                </tr>
                <tr>
                    <td style="padding: 5px; font-weight: bold;">Completion:</td>
                    <td style="padding: 5px;">
                        <div style="width: 200px; height: 20px; background: #e5e7eb; border-radius: 10px;">
                            <div style="width: {obj.completion_percentage}%; height: 100%; 
                                       background: #10b981; border-radius: 10px;"></div>
                        </div>
                        {obj.completion_percentage}%
                    </td>
                </tr>
            </table>
        </div>
        '''
        return mark_safe(html)
    detailed_info.short_description = 'Detailed Information'
    
    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} classification(s) marked as completed.')
    mark_as_completed.short_description = 'Mark as Completed'
    
    def mark_as_failed(self, request, queryset):
        updated = queryset.update(status='failed')
        self.message_user(request, f'{updated} classification(s) marked as failed.')
    mark_as_failed.short_description = 'Mark as Failed'
    
    def reprocess_classification(self, request, queryset):
        updated = queryset.update(status='pending')
        self.message_user(request, f'{updated} classification(s) queued for reprocessing.')
    reprocess_classification.short_description = 'Reprocess Classification'


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'question_number',
        'classification_link',
        'category_badge',
        'formatted_confidence',
        'question_preview',
    ]
    
    list_filter = [
        'category',
        'classification__status',
        'created_at',
    ]
    
    search_fields = [
        'question_text',
        'classification__filename',
        'classification__user__username',
    ]
    
    readonly_fields = [
        'created_at',
        'question_preview_full',
    ]
    
    fieldsets = (
        ('Classification', {
            'fields': ('classification', 'question_number')
        }),
        ('Question Details', {
            'fields': ('question_text', 'category', 'confidence_score')
        }),
        ('Answer Choices', {
            'fields': ('choice_a', 'choice_b', 'choice_c', 'choice_d', 'choice_e'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'question_preview_full'),
            'classes': ('collapse',)
        }),
    )
    
    def classification_link(self, obj):
        url = reverse('admin:klasifikasi_classification_change', args=[obj.classification.id])
        return format_html('<a href="{}">{}</a>', url, obj.classification.filename)
    classification_link.short_description = 'Classification'
    
    def category_badge(self, obj):
        color_map = {
            'C1': '#10b981',
            'C2': '#3b82f6',
            'C3': '#eab308',
            'C4': '#f97316',
            'C5': '#a855f7',
            'C6': '#ef4444',
        }
        color = color_map.get(obj.category, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_category_display()
        )
    category_badge.short_description = 'Category'
    
    def question_preview(self, obj):
        preview = obj.question_text[:50] + '...' if len(obj.question_text) > 50 else obj.question_text
        return preview
    question_preview.short_description = 'Question Preview'
    
    def question_preview_full(self, obj):
        html = f'''
        <div style="padding: 10px; background: #f9fafb; border-radius: 5px; max-width: 800px;">
            <h4 style="margin-top: 0;">Question {obj.question_number}</h4>
            <p style="font-size: 14px; line-height: 1.6;">{obj.question_text}</p>
            
            <h5>Classification</h5>
            <p><strong>Category:</strong> {obj.get_category_display()}</p>
            <p><strong>Confidence:</strong> {obj.formatted_confidence}</p>
        '''
        
        if any([obj.choice_a, obj.choice_b, obj.choice_c, obj.choice_d, obj.choice_e]):
            html += '<h5>Answer Choices</h5><ul>'
            for letter, choice in [('A', obj.choice_a), ('B', obj.choice_b), 
                                   ('C', obj.choice_c), ('D', obj.choice_d), ('E', obj.choice_e)]:
                if choice:
                    html += f'<li><strong>{letter}.</strong> {choice}</li>'
            html += '</ul>'
        
        html += '</div>'
        return mark_safe(html)
    question_preview_full.short_description = 'Full Question Preview'


# Custom admin site configuration
admin.site.site_header = "Bloomers Admin"
admin.site.site_title = "Bloomers Admin Portal"
admin.site.index_title = "Welcome to Bloomers Administration"
"""