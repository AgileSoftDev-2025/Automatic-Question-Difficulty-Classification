from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.contrib.auth.forms import PasswordChangeForm
from django.utils import timezone
from PIL import Image
import os
import logging
import re

from .models import User, Profile

logger = logging.getLogger(__name__)


def validate_password_strength(password):
    """
    Validate password strength.
    Returns tuple: (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    
    # Optional: Add more strength requirements
    has_upper = re.search(r'[A-Z]', password)
    has_lower = re.search(r'[a-z]', password)
    has_digit = re.search(r'\d', password)
    
    if not (has_upper and has_lower and has_digit):
        return False, "Password must contain uppercase, lowercase, and numbers."
    
    return True, ""


@csrf_protect
def login_view(request):
    """
    Handle user login with email and password.
    Redirects authenticated users to home page.
    """
    # Redirect if already logged in
    if request.user.is_authenticated:
        messages.info(request, 'You are already logged in.')
        return redirect('soal:home')
    
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        remember = request.POST.get('remember', False)
        
        # Validation
        if not email or not password:
            messages.error(request, 'Please provide both email and password.')
            logger.warning(f"Login attempt with missing credentials from IP: {request.META.get('REMOTE_ADDR')}")
            return render(request, 'users/login.html')
        
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Please enter a valid email address.')
            logger.warning(f"Login attempt with invalid email format: {email}")
            return render(request, 'users/login.html')
        
        # Check if user exists first (for better error messages)
        try:
            user_exists = User.objects.filter(email__iexact=email).exists()
            if not user_exists:
                messages.error(request, 'Invalid email or password. Please try again.')
                logger.warning(f"Login attempt with non-existent email: {email}")
                return render(request, 'users/login.html')
        except Exception as e:
            logger.error(f"Error checking user existence: {e}")
        
        # Authenticate using email as username
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            if user.is_active:
                login(request, user)
                
                # Handle "remember me" functionality
                if not remember:
                    request.session.set_expiry(0)  # Session expires when browser closes
                else:
                    request.session.set_expiry(1209600)  # 2 weeks
                
                # Update last login time
                user.last_login = timezone.now()
                user.save(update_fields=['last_login'])
                
                messages.success(request, f'Welcome back, {user.username}!')
                logger.info(f"Successful login for user: {user.username} ({user.email})")
                
                # Redirect to next parameter or home
                next_page = request.GET.get('next', 'soal:home')
                
                # Security: Validate next parameter to prevent open redirect
                if next_page and (next_page.startswith('/') or next_page.startswith('http')):
                    if not next_page.startswith('http'):
                        return redirect(next_page)
                
                return redirect('soal:home')
            else:
                messages.error(request, 'Your account has been disabled. Please contact support.')
                logger.warning(f"Login attempt for disabled account: {email}")
        else:
            messages.error(request, 'Invalid email or password. Please try again.')
            logger.warning(f"Failed login attempt for email: {email}")
    
    return render(request, 'users/login.html')


@csrf_protect
def register_view(request):
    """
    Handle user registration with username, email, and password.
    Automatically logs in user after successful registration.
    """
    # Redirect if already logged in
    if request.user.is_authenticated:
        messages.info(request, 'You already have an account.')
        return redirect('soal:home')
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        
        # Basic validation
        if not all([username, email, password, confirm_password]):
            messages.error(request, 'All fields are required.')
            return render(request, 'users/register.html')
        
        # Username validation
        if len(username) < 3:
            messages.error(request, 'Username must be at least 3 characters long.')
            return render(request, 'users/register.html')
        
        if len(username) > 150:
            messages.error(request, 'Username must be less than 150 characters.')
            return render(request, 'users/register.html')
        
        # Check for invalid characters in username
        if not re.match(r'^[\w.@+-]+$', username):
            messages.error(request, 'Username can only contain letters, numbers, and @/./+/-/_ characters.')
            return render(request, 'users/register.html')
        
        # Email validation
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Please enter a valid email address.')
            return render(request, 'users/register.html')
        
        # Password validation
        if len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return render(request, 'users/register.html')
        
        # Validate password strength
        is_valid, error_msg = validate_password_strength(password)
        if not is_valid:
            messages.error(request, error_msg)
            return render(request, 'users/register.html')
        
        # Confirm password match
        if password != confirm_password:
            messages.error(request, 'Passwords do not match. Please try again.')
            return render(request, 'users/register.html')
        
        # Check if username already exists (case-insensitive)
        if User.objects.filter(username__iexact=username).exists():
            messages.error(request, 'Username already taken. Please choose another one.')
            logger.warning(f"Registration attempt with existing username: {username}")
            return render(request, 'users/register.html')
        
        # Check if email already exists (case-insensitive)
        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, 'Email already registered. Please use another email or login.')
            logger.warning(f"Registration attempt with existing email: {email}")
            return render(request, 'users/register.html')
        
        # Create user with transaction
        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )
                
                # Profile is created automatically via signal
                # But we can ensure it exists
                Profile.objects.get_or_create(user=user)
                
                # Auto login after registration
                login(request, user)
                
                messages.success(request, f'Welcome to Bloomers, {username}! Your account has been created successfully.')
                logger.info(f"New user registered: {username} ({email})")
                
                return redirect('soal:home')
                
        except IntegrityError as e:
            messages.error(request, 'An account with this username or email already exists.')
            logger.error(f"IntegrityError during registration: {e}")
        except Exception as e:
            messages.error(request, f'An error occurred during registration. Please try again.')
            logger.error(f"Unexpected error during registration: {e}", exc_info=True)
    
    return render(request, 'users/register.html')


@login_required(login_url='users:login')
def logout_view(request):
    """
    Handle user logout.
    Requires user to be logged in.
    """
    username = request.user.username
    user_email = request.user.email
    
    logout(request)
    
    messages.success(request, f'Goodbye, {username}! You have been logged out successfully.')
    logger.info(f"User logged out: {username} ({user_email})")
    
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
        email = request.POST.get('email', '').strip().lower()
        
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
            # from django.core.mail import send_mail
            # from django.contrib.auth.tokens import default_token_generator
            # from django.utils.http import urlsafe_base64_encode
            # from django.utils.encoding import force_bytes
            
            logger.info(f"Password reset requested for: {email}")
            messages.success(request, 'If an account exists with this email, you will receive a password reset link shortly.')
            return redirect('users:login')
            
        except User.DoesNotExist:
            # Don't reveal if email exists or not (security)
            logger.warning(f"Password reset requested for non-existent email: {email}")
            messages.success(request, 'If an account exists with this email, you will receive a password reset link shortly.')
            return redirect('users:login')
        except Exception as e:
            logger.error(f"Error in password reset request: {e}", exc_info=True)
            messages.error(request, 'An error occurred. Please try again later.')
    
    return render(request, 'users/password_reset_request.html')


@login_required(login_url='users:login')
@csrf_protect
@transaction.atomic
def profile_view(request):
    """
    Display and manage user profile updates.
    Handles 3 separate forms: details, password change, and profile picture.
    """
    # Ensure profile exists
    profile_obj, created = Profile.objects.get_or_create(user=request.user)
    if created:
        logger.info(f"Profile created for user: {request.user.username}")
    
    password_form = PasswordChangeForm(request.user)

    if request.method == 'POST':
        
        # --- 1. Profile Details Form (first_name, last_name, email) ---
        if 'email' in request.POST and 'first_name' in request.POST and \
           'profile_image' not in request.FILES and 'remove_image' not in request.POST and \
           'old_password' not in request.POST:
            
            try:
                user = request.user
                first_name = request.POST.get('first_name', '').strip()
                last_name = request.POST.get('last_name', '').strip()
                email = request.POST.get('email', '').strip().lower()
                
                # Validate names (optional)
                if first_name and len(first_name) > 150:
                    messages.error(request, 'First name is too long (max 150 characters).')
                    return redirect('users:profile')
                
                if last_name and len(last_name) > 150:
                    messages.error(request, 'Last name is too long (max 150 characters).')
                    return redirect('users:profile')
                
                # Validate email
                try:
                    validate_email(email)
                except ValidationError:
                    messages.error(request, 'Please enter a valid email address.')
                    return redirect('users:profile')
                
                # Check for duplicate email
                if User.objects.filter(email__iexact=email).exclude(id=user.id).exists():
                    messages.error(request, 'This email is already in use by another account.')
                    logger.warning(f"Profile update attempt with duplicate email: {email}")
                    return redirect('users:profile')
                
                # Update user details
                user.first_name = first_name
                user.last_name = last_name
                user.email = email
                user.save(update_fields=['first_name', 'last_name', 'email'])
                
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
                # Display form errors
                for field, errors in password_form.errors.items():
                    for error in errors:
                        messages.error(request, f"{error}")
                
                logger.warning(f"Password change failed for user: {request.user.username}")
            
            return redirect('users:profile')

        # --- 3. Upload Profile Picture ---
        elif 'profile_image' in request.FILES:
            uploaded_file = request.FILES['profile_image']
            
            try:
                # Validate file type
                ext = uploaded_file.name.split('.')[-1].lower()
                allowed_extensions = ['jpg', 'jpeg', 'png']
                
                if ext not in allowed_extensions:
                    messages.error(request, f'Invalid file format. Only {", ".join(allowed_extensions).upper()} are allowed.')
                    return redirect('users:profile')
                
                # Validate file size (max 2MB)
                max_size = 2 * 1024 * 1024  # 2MB in bytes
                if uploaded_file.size > max_size:
                    messages.error(request, 'File is too large. Maximum size is 2MB.')
                    logger.warning(f"Large file upload attempt by {request.user.username}: {uploaded_file.size} bytes")
                    return redirect('users:profile')
                
                # Validate it's actually an image
                try:
                    img = Image.open(uploaded_file)
                    img.verify()
                    uploaded_file.seek(0)  # Reset file pointer after verify
                except Exception:
                    messages.error(request, 'Invalid image file.')
                    logger.warning(f"Invalid image upload attempt by {request.user.username}")
                    return redirect('users:profile')
                
                # Delete old image if it exists
                if profile_obj.has_custom_image:
                    try:
                        old_image_path = profile_obj.image.path
                        if os.path.exists(old_image_path):
                            os.remove(old_image_path)
                            logger.info(f"Deleted old profile image: {old_image_path}")
                    except Exception as e:
                        logger.warning(f"Could not delete old profile image: {e}")
                
                # Save new image
                profile_obj.image = uploaded_file
                profile_obj.save()
                
                # Resize image to optimize storage
                try:
                    img = Image.open(profile_obj.image.path)
                    
                    # Convert RGBA to RGB if necessary
                    if img.mode in ('RGBA', 'LA', 'P'):
                        rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                        rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                        img = rgb_img
                    
                    # Resize if too large
                    max_dimension = 500
                    if img.height > max_dimension or img.width > max_dimension:
                        img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
                        img.save(profile_obj.image.path, quality=85, optimize=True)
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
                # Refresh profile from database
                profile_obj = Profile.objects.get(user=request.user)
                
                if profile_obj.has_custom_image:
                    # Delete physical file
                    try:
                        if profile_obj.image and hasattr(profile_obj.image, 'path'):
                            image_path = profile_obj.image.path
                            if os.path.exists(image_path):
                                os.remove(image_path)
                                logger.info(f"Deleted profile image file: {image_path}")
                    except Exception as e:
                        logger.warning(f"Could not delete image file: {e}")
                    
                    # Clear the image field
                    profile_obj.image.delete(save=False)
                    profile_obj.image = None
                    profile_obj.save()
                    
                    # Verify it was cleared
                    profile_obj.refresh_from_db()
                    
                    if not profile_obj.has_custom_image:
                        logger.info(f"Profile picture removed for user: {request.user.username}")
                        messages.success(request, 'Profile picture removed successfully.')
                    else:
                        logger.error(f"Image field not cleared for user: {request.user.username}")
                        messages.error(request, 'Failed to remove profile picture. Please try again.')
                else:
                    logger.info(f"User {request.user.username} already using default avatar")
                    messages.info(request, 'You are already using the default avatar.')
                    
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