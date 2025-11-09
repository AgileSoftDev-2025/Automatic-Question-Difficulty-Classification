"""
URL Configuration for Klasifikasi App
"""

from django.urls import path
from . import views

app_name = 'klasifikasi'

urlpatterns = [
    # Main pages
    path('', views.home, name='home'),
    path('history/', views.history_view, name='history'),
    path('hasil/<int:pk>/', views.hasil_klasifikasi, name='hasil_klasifikasi'),
    
    # Classification management
    path('detail/<int:pk>/', views.view_classification_detail, name='view_detail'),
    path('delete/<int:pk>/', views.delete_classification, name='delete'),
    path('bulk-delete/', views.bulk_delete_classifications, name='bulk_delete'),
    
    # Reports
    path('report/<int:pk>/', views.view_report, name='view_report'),
    path('download/<int:pk>/', views.download_report, name='download_report'),
    
    # API endpoints (AJAX)
    path('api/stats/', views.get_classification_stats, name='api_stats'),
    path('api/update-question/<int:pk>/', views.update_question_classification, name='update_question'),
]