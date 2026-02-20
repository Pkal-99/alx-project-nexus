import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserRole(models.TextChoices):
    GUEST = 'guest', _('Guest')
    USER = 'user', _('User')
    MODERATOR = 'moderator', _('Moderator')
    ADMIN = 'admin', _('Admin')


class User(AbstractUser):
    """
    Custom User model with UUID primary key and role-based permissions.
    Optimized for millions of users with proper indexing.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_('email address'), unique=True)
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.USER,
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['email'], name='idx_user_email'),
            models.Index(fields=['username'], name='idx_user_username'),
            models.Index(fields=['role', 'created_at'], name='idx_user_role_created'),
            models.Index(fields=['is_active', 'created_at'], name='idx_user_active_created'),
        ]
    
    def __str__(self):
        return f"@{self.username}"


class Profile(models.Model):
    """
    User profile with one-to-one relationship to User.
    Includes settings, bio, and avatar management.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        db_index=True
    )
    bio = models.TextField(max_length=500, blank=True)
    avatar_url = models.URLField(max_length=500, blank=True)
    settings = models.JSONField(default=dict, blank=True)
    followers_count = models.PositiveIntegerField(default=0)
    following_count = models.PositiveIntegerField(default=0)
    posts_count = models.PositiveIntegerField(default=0)
    is_private = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'profiles'
        indexes = [
            models.Index(fields=['user'], name='idx_profile_user'),
            models.Index(fields=['is_private', 'created_at'], name='idx_profile_private_created'),
        ]
    
    def __str__(self):
        return f"{self.user.username}'s profile"
