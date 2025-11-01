from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, get_user_model, logout
from django.contrib import messages

@csrf_protect
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('soal:home')
        else:
            messages.error(request, 'Invalid email or password')
    
    return render(request, 'users/login.html')

@csrf_protect
def register_view(request):
    User = get_user_model()
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password1')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered')
            return render(request, 'users/register.html')
            
        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            login(request, user)
            return redirect('soal:home')
        except Exception as e:
            messages.error(request, str(e))
            
    return render(request, 'users/register.html')

def logout_view(request):
    """Menangani proses logout pengguna."""
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('soal:home')