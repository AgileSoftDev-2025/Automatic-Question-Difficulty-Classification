from django.urls import path
from . import views

app_name = 'soal'

urlpatterns = [
    path('', views.home, name='home'),
]