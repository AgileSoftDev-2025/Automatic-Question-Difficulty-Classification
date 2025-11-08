from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, get_user_model, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db import IntegrityError

User = get_user_model()

@csrf_protect
def login_view(request):
    """
    Handle user login with email and password.
    Redirects authenticated users to home page.
    """
    # Redirect if user is already logged in
    if request.user.is_authenticated:
        messages.info(request, 'You are already logged in.')
        return redirect('soal:home')
    
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        
        # Validate input
        if not email or not password:
            messages.error(request, 'Please provide both email and password.')
            return render(request, 'users/login.html')
        
        # Validate email format
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Please enter a valid email address.')
            return render(request, 'users/login.html')
        
        # Authenticate user
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            if user.is_active:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                
                # Redirect to next page if provided, otherwise to home
                next_page = request.GET.get('next', 'soal:home')
                return redirect(next_page)
            else:
                messages.error(request, 'Your account has been disabled.')
        else:
            messages.error(request, 'Invalid email or password. Please try again.')
    
    return render(request, 'users/login.html')


@csrf_protect
def register_view(request):
    """
    Handle user registration with username, email, and password.
    Automatically logs in user after successful registration.
    """
    # Redirect if user is already logged in
    if request.user.is_authenticated:
        messages.info(request, 'You already have an account.')
        return redirect('soal:home')
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        
        # Validate all fields are provided
        if not all([username, email, password]):
            messages.error(request, 'All fields are required.')
            return render(request, 'users/register.html')
        
        # Validate username length
        if len(username) < 3:
            messages.error(request, 'Username must be at least 3 characters long.')
            return render(request, 'users/register.html')
        
        if len(username) > 150:
            messages.error(request, 'Username must be less than 150 characters.')
            return render(request, 'users/register.html')
        
        # Validate email format
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Please enter a valid email address.')
            return render(request, 'users/register.html')
        
        # Validate password strength
        if len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return render(request, 'users/register.html')
        
        # Check if username already exists
        if User.objects.filter(username__iexact=username).exists():
            messages.error(request, 'Username already taken. Please choose another one.')
            return render(request, 'users/register.html')
        
        # Check if email already exists
        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, 'Email already registered. Please use another email or login.')
            return render(request, 'users/register.html')
        
        # Create user
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            
            # Auto login after registration
            login(request, user)
            messages.success(request, f'Welcome to Bloomers, {username}! Your account has been created successfully.')
            return redirect('soal:home')
            
        except IntegrityError:
            messages.error(request, 'An account with this username or email already exists.')
        except Exception as e:
            messages.error(request, f'An error occurred during registration: {str(e)}')
    
    return render(request, 'users/register.html')


@login_required(login_url='users:login')
def logout_view(request):
    """
    Handle user logout.
    Requires user to be logged in.
    """
    username = request.user.username
    logout(request)
    messages.success(request, f'Goodbye, {username}! You have been logged out successfully.')
    return redirect('users:login')


# Optional: Password Reset Request View
@csrf_protect
def password_reset_request_view(request):
    """
    Handle password reset request.
    Sends reset link to user's email.
    """
    if request.user.is_authenticated:
        messages.info(request, 'You are already logged in.')
        return redirect('soal:home')
    
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        
        if not email:
            messages.error(request, 'Please provide your email address.')
            return render(request, 'users/password_reset_request.html')
        
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Please enter a valid email address.')
            return render(request, 'users/password_reset_request.html')
        
        # Check if user exists
        try:
            user = User.objects.get(email__iexact=email)
            # TODO: Implement email sending logic here
            # For now, just show success message
            messages.success(request, 'If an account exists with this email, you will receive a password reset link shortly.')
            return redirect('users:login')
        except User.DoesNotExist:
            # Don't reveal if email exists or not (security best practice)
            messages.success(request, 'If an account exists with this email, you will receive a password reset link shortly.')
            return redirect('users:login')
    
    return render(request, 'users/password_reset_request.html')


# Optional: User Profile View
@login_required(login_url='users:login')
def profile_view(request):
    """
    Display user profile information.
    """
    return render(request, 'users/profile.html', {
        'user': request.user
    })