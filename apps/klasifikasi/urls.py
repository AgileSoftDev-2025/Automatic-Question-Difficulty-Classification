# apps/klasifikasi/urls.py

from django.urls import path
from . import views

app_name = 'klasifikasi'

urlpatterns = [
    # Home redirect
    path('', views.redirect_to_main_home, name='home'),
    
    # Classification results
    path('hasil/<int:pk>/', views.hasil_klasifikasi, name='hasil_klasifikasi'),
    
    # History
    path('history/', views.history_view, name='history'),
    
    # CRUD operations
    path('delete/<int:pk>/', views.delete_classification, name='delete'),
    path('update/<int:pk>/', views.update_question_classification, name='update'),
    
    # Exports
    path('download/<int:pk>/', views.download_report, name='download_report'),
    path('export/<int:pk>/', views.export_classification_excel, name='export_excel'),
    
    # API endpoints
    path('api/stats/', views.get_classification_stats, name='stats'),
    path('api/question/<int:classification_id>/<int:question_id>/', 
         views.get_question_details, name='question_details'),
    
    # Bulk operations
    path('bulk-delete/', views.bulk_delete_classifications, name='bulk_delete'),
    
    # Analytics
    path('analytics/<int:pk>/', views.classification_analytics, name='analytics'),
    
    # Reprocess
    path('reprocess/<int:pk>/', views.reprocess_classification, name='reprocess'),
]