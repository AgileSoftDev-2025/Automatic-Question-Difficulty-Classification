from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
import os


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    Uses email for authentication instead of username.
    """
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    
    # Override USERNAME_FIELD to use email for authentication
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return self.email
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'


def user_profile_image_path(instance, filename):
    """
    Generate upload path for profile images.
    Format: profile_pics/user_{user_id}/{filename}
    """
    ext = filename.split('.')[-1]
    filename = f'profile_{instance.user.id}.{ext}'
    return os.path.join('profile_pics', f'user_{instance.user.id}', filename)


class Profile(models.Model):
    """
    User Profile model to store additional user information.
    Automatically created when a new user registers.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Profile image with custom upload path - NO DEFAULT, will use letter avatar
    image = models.ImageField(
        upload_to=user_profile_image_path,
        blank=True,
        null=True,
        help_text='Profile picture (max 2MB, JPG/PNG)'
    )
    
    bio = models.TextField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Notification Preferences
    notif_classification = models.BooleanField(default=True)
    notif_updates = models.BooleanField(default=False)
    notif_tips = models.BooleanField(default=True)
    notif_marketing = models.BooleanField(default=False)
    
    # Application Preferences
    language = models.CharField(max_length=10, default='en')
    timezone = models.CharField(max_length=50, default='Asia/Jakarta')
    results_per_page = models.IntegerField(default=25)
    auto_download = models.BooleanField(default=False)
    show_tutorials = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    @property
    def has_custom_image(self):
        """
        Check if user has uploaded a custom profile picture.
        Returns False if no image or if image field is empty/invalid.
        """
        if not self.image:
            return False
        
        # Try to access image.name to verify it's valid
        try:
            # Check if image has a name and it's not empty
            image_name = self.image.name
            return bool(image_name and len(image_name.strip()) > 0)
        except (ValueError, AttributeError, OSError):
            # Image field exists but file is missing or invalid
            return False
    
    @property
    def avatar_letter(self):
        """
        Get the first letter of username for avatar display.
        """
        return self.user.username[0].upper() if self.user.username else '?'
    
    def delete_image(self):
        """
        Delete the profile image file from storage.
        """
        if self.image:
            try:
                image_path = self.image.path
                if os.path.exists(image_path):
                    os.remove(image_path)
                    return True
            except Exception as e:
                print(f"Error deleting image: {e}")
        return False
    
    class Meta:
        db_table = 'profiles'
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Automatically create a Profile when a new User is created.
    """
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Automatically save the Profile when the User is saved.
    """
    if hasattr(instance, 'profile'):
        instance.profile.save()