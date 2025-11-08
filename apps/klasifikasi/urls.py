from django.urls import path
from . import views

app_name = 'klasifikasi'

urlpatterns = [
    path('', views.index, name='klasifikasi_index'),
    path('hasil/', views.index, name='klasifikasi_hasil'),
    # History URLs
    path('history/', views.history_view, name='history'),
    path('classification/<int:pk>/delete/', views.delete_classification, name='delete_classification'),
    path('<int:pk>/detail/', views.view_classification_detail, name='classification_detail'),
    path('classification/<int:pk>/download/', views.download_report, name='download_report'),
    path('classification/<int:pk>/report/', views.view_report, name='view_report'),
]
