# ===================================
# FILE: urls.py (untuk app klasifikasi)
# Path: Automatic-Question-Difficulty-Classification/apps/klasifikasi/urls.py
# ===================================

from django.urls import path
from . import views

app_name = 'klasifikasi'

urlpatterns = [
    # Main pages
    path('', views.home, name='home'),
    path('history/', views.history_view, name='history'),
    
    # Classification operations
    path('detail/<int:pk>/', views.view_classification_detail, name='view_detail'),
    path('delete/<int:pk>/', views.delete_classification, name='delete'),
    path('bulk-delete/', views.bulk_delete_classifications, name='bulk_delete'),
    
    # Report operations
    path('report/<int:pk>/', views.view_report, name='view_report'),
    path('download/<int:pk>/', views.download_report, name='download_report'),
    
    # API endpoints
    path('api/stats/', views.get_classification_stats, name='api_stats'),
]