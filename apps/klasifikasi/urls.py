"""
URL Configuration for Klasifikasi App
"""

from django.urls import path
from . import views

app_name = 'klasifikasi'

urlpatterns = [
    # Home page
    path('', views.home, name='home'),
    
    # Classification results
    path('hasil/<int:pk>/', views.hasil_klasifikasi, name='hasil_klasifikasi'),
    
    # History
    path('history/', views.history_view, name='history'),
    
    # Update question classification (AJAX)
    path('update/<int:pk>/', views.update_question_classification, name='update_classification'),
    
    # Delete classification
    path('delete/<int:pk>/', views.delete_classification, name='delete_classification'),
    
    # Bulk delete
    path('bulk-delete/', views.bulk_delete_classifications, name='bulk_delete'),
    
    # Download report
    path('download/<int:pk>/', views.download_report, name='download_report'),
    
    # Export to Excel
    path('export/<int:pk>/', views.export_classification_excel, name='export_excel'),
    
    # API endpoints
    path('api/stats/', views.get_classification_stats, name='api_stats'),
    path('api/question/<int:classification_id>/<int:question_id>/', views.get_question_details, name='question_details'),
    
    # Analytics
    path('analytics/<int:pk>/', views.classification_analytics, name='analytics'),
]