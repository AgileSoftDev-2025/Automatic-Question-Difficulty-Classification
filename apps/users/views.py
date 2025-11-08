from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, get_user_model, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.contrib.auth.forms import PasswordChangeForm
import logging
from PIL import Image
import os

# Impor model Anda
from .models import User, Profile 

logger = logging.getLogger(__name__)


@csrf_protect
def login_view(request):
    """
    Handle user login with email and password.
    Redirects authenticated users to home page.
    """
    if request.user.is_authenticated:
        messages.info(request, 'You are already logged in.')
        return redirect('soal:home')
    
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        
        if not email or not password:
            messages.error(request, 'Please provide both email and password.')
            return render(request, 'users/login.html')
        
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Please enter a valid email address.')
            return render(request, 'users/login.html')
        
        # Otentikasi menggunakan 'email' sebagai username
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            if user.is_active:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                
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
    if request.user.is_authenticated:
        messages.info(request, 'You already have an account.')
        return redirect('soal:home')
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        
        if not all([username, email, password]):
            messages.error(request, 'All fields are required.')
            return render(request, 'users/register.html')
        
        if len(username) < 3:
            messages.error(request, 'Username must be at least 3 characters long.')
            return render(request, 'users/register.html')
        
        if len(username) > 150:
            messages.error(request, 'Username must be less than 150 characters.')
            return render(request, 'users/register.html')
        
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Please enter a valid email address.')
            return render(request, 'users/register.html')
        
        if len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return render(request, 'users/register.html')
        
        if User.objects.filter(username__iexact=username).exists():
            messages.error(request, 'Username already taken. Please choose another one.')
            return render(request, 'users/register.html')
        
        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, 'Email already registered. Please use another email or login.')
            return render(request, 'users/register.html')
        
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
        
        try:
            user = User.objects.get(email__iexact=email)
            # TODO: Implement email sending logic here
            messages.success(request, 'If an account exists with this email, you will receive a password reset link shortly.')
            return redirect('users:login')
        except User.DoesNotExist:
            messages.success(request, 'If an account exists with this email, you will receive a password reset link shortly.')
            return redirect('users:login')
    
    return render(request, 'users/password_reset_request.html')

@login_required(login_url='users:login')
@csrf_protect
@transaction.atomic
def profile_view(request):
    """
    Display and manage user profile updates.
    Handles 3 separate forms: details, password change, and profile picture.
    """
    profile_obj, created = Profile.objects.get_or_create(user=request.user)
    password_form = PasswordChangeForm(request.user)

    if request.method == 'POST':
        
        # --- 1. Profile Details Form (first_name, last_name, email) ---
        if 'email' in request.POST and 'first_name' in request.POST and 'profile_image' not in request.FILES and 'remove_image' not in request.POST and 'old_password' not in request.POST:
            try:
                user = request.user
                first_name = request.POST.get('first_name', '').strip()
                last_name = request.POST.get('last_name', '').strip()
                email = request.POST.get('email', '').strip()
                
                # Validate email
                try:
                    validate_email(email)
                except ValidationError:
                    messages.error(request, 'Please enter a valid email address.')
                    return redirect('users:profile')
                
                # Check for duplicate email
                if User.objects.filter(email__iexact=email).exclude(id=user.id).exists():
                    messages.error(request, 'This email is already in use by another account.')
                    return redirect('users:profile')
                
                user.first_name = first_name
                user.last_name = last_name
                user.email = email
                user.save()
                
                logger.info(f"Profile details updated for user: {user.username}")
                messages.success(request, 'Profile details updated successfully.')
                
            except Exception as e:
                logger.error(f"Error updating profile details for {request.user.username}: {e}", exc_info=True)
                messages.error(request, "Failed to update profile details. Please try again.")
            
            return redirect('users:profile')

        # --- 2. Password Change Form ---
        elif 'old_password' in request.POST and 'new_password1' in request.POST:
            password_form = PasswordChangeForm(request.user, request.POST)
            
            if password_form.is_valid():
                try:
                    user = password_form.save()
                    update_session_auth_hash(request, user)
                    logger.info(f"Password changed successfully for user: {user.username}")
                    messages.success(request, 'Your password was successfully updated!')
                except Exception as e:
                    logger.error(f"Error changing password for {request.user.username}: {e}", exc_info=True)
                    messages.error(request, 'An error occurred while updating your password.')
            else:
                for field, errors in password_form.errors.items():
                    for error in errors:
                        messages.error(request, f"{error}")
                if not password_form.errors:
                    messages.error(request, 'Password change failed. Please correct the errors.')
            
            return redirect('users:profile')

        # --- 3. Upload Profile Picture ---
        elif 'profile_image' in request.FILES:
            uploaded_file = request.FILES['profile_image']
            
            try:
                # Validate file type
                ext = uploaded_file.name.split('.')[-1].lower()
                if ext not in ['jpg', 'jpeg', 'png']:
                    messages.error(request, 'Invalid file format. Only JPG, JPEG, or PNG are allowed.')
                    return redirect('users:profile')
                
                # Validate file size (max 2MB)
                max_size = 2 * 1024 * 1024  # 2MB in bytes
                if uploaded_file.size > max_size:
                    messages.error(request, 'File is too large. Maximum size is 2MB.')
                    return redirect('users:profile')
                
                # Validate it's actually an image
                try:
                    img = Image.open(uploaded_file)
                    img.verify()
                    uploaded_file.seek(0)  # Reset file pointer after verify
                except Exception:
                    messages.error(request, 'Invalid image file.')
                    return redirect('users:profile')
                
                # Delete old image if it exists and is not default
                if profile_obj.image:
                    old_image_path = profile_obj.image.path
                    if os.path.exists(old_image_path) and 'default.jpg' not in old_image_path:
                        try:
                            os.remove(old_image_path)
                            logger.info(f"Deleted old profile image: {old_image_path}")
                        except Exception as e:
                            logger.warning(f"Could not delete old profile image: {e}")
                
                # Save new image
                profile_obj.image = uploaded_file
                profile_obj.save()
                
                # Optional: Resize image to optimize storage
                try:
                    img = Image.open(profile_obj.image.path)
                    if img.height > 500 or img.width > 500:
                        output_size = (500, 500)
                        img.thumbnail(output_size, Image.Resampling.LANCZOS)
                        img.save(profile_obj.image.path)
                        logger.info(f"Resized profile image for user: {request.user.username}")
                except Exception as e:
                    logger.warning(f"Could not resize image: {e}")
                
                logger.info(f"Profile picture updated for user: {request.user.username}")
                messages.success(request, 'Profile picture updated successfully.')
                
            except Exception as e:
                logger.error(f"Error uploading profile picture for {request.user.username}: {e}", exc_info=True)
                messages.error(request, 'Failed to upload profile picture. Please try again.')
            
            return redirect('users:profile')

        # --- 4. Remove Profile Picture ---
        elif 'remove_image' in request.POST:
            try:
                # Check if user has a non-default image
                if profile_obj.image:
                    image_path = profile_obj.image.path
                    image_name = profile_obj.image.name
                    
                    # Check if it's not the default image
                    if 'default.jpg' not in image_name:
                        # Delete the file from storage
                        if os.path.exists(image_path):
                            try:
                                os.remove(image_path)
                                logger.info(f"Deleted profile image file: {image_path}")
                            except Exception as e:
                                logger.warning(f"Could not delete profile image file: {e}")
                        
                        # Set to default
                        profile_obj.image = 'profile_pics/default.jpg'
                        profile_obj.save()
                        
                        logger.info(f"Profile picture removed for user: {request.user.username}")
                        messages.success(request, 'Profile picture removed successfully.')
                    else:
                        messages.info(request, 'You are already using the default profile picture.')
                else:
                    messages.info(request, 'You are already using the default profile picture.')
                    
            except Exception as e:
                logger.error(f"Error removing profile picture for {request.user.username}: {e}", exc_info=True)
                messages.error(request, 'Failed to remove profile picture. Please try again.')
            
            return redirect('users:profile')

    # GET request
    context = {
        'user': request.user,
        'profile': profile_obj,
        'password_form': password_form,
    }
    
    return render(request, 'users/profile.html', context)