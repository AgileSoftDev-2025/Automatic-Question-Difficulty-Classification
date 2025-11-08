# apps/soal/urls.py

from django.urls import path
from . import views

app_name = 'soal'

urlpatterns = [
    # Home page with file upload
    path('', views.home, name='home'),
    path('help/', views.help_faq, name='help'),
    
    # File management
    path('download/<int:history_id>/', views.download_file, name='download_file'),
    path('delete/<int:history_id>/', views.delete_history, name='delete_history'),
    path('clear-history/', views.clear_all_history, name='clear_history'),
    
    # Optional AJAX endpoint
    path('api/validate-file/', views.validate_file_ajax, name='validate_file_ajax'),
]