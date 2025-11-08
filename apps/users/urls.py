from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Optional
    path('password-reset/', views.password_reset_request_view, name='password_reset'),
    path('profile/', views.profile_view, name='profile'),
]