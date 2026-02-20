import uuid
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from profiles.models import User


class PostStatus(models.TextChoices):
    DRAFT = 'draft', _('Draft')
    PUBLISHED = 'published', _('Published')
    SCHEDULED = 'scheduled', _('Scheduled')
    DELETED = 'deleted', _('Deleted')


class Post(models.Model):
    """
    Post model with soft-delete strategy and status management.
    Optimized for feed generation with proper indexing.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        db_index=True
    )
    content_text = models.TextField(max_length=2000, blank=True)
    status = models.CharField(
        max_length=20,
        choices=PostStatus.choices,
        default=PostStatus.DRAFT,
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    published_at = models.DateTimeField(null=True, blank=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)
    
    # Engagement metrics for quick access
    likes_count = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)
    shares_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'posts'
        indexes = [
            models.Index(fields=['user', 'status', 'created_at'], name='idx_post_user_status_created'),
            models.Index(fields=['status', 'published_at'], name='idx_post_status_published'),
            models.Index(fields=['created_at'], name='idx_post_created'),
            models.Index(fields=['deleted_at'], name='idx_post_deleted'),
            models.Index(fields=['likes_count', 'created_at'], name='idx_post_likes_created'),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Post by {self.user.username} at {self.created_at}"


class Follow(models.Model):
    """
    Social graph model for following relationships.
    Composite indexes for optimal follower/following queries.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        db_index=True
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followers',
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'follows'
        unique_together = ['follower', 'following']
        indexes = [
            models.Index(fields=['follower', 'created_at'], name='idx_follow_follower_created'),
            models.Index(fields=['following', 'created_at'], name='idx_follow_following_created'),
            models.Index(fields=['follower', 'following'], name='idx_follow_pair'),
        ]
    
    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"


class Comment(models.Model):
    """
    Comment model with nested replies support.
    Soft-delete strategy for content moderation.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        db_index=True
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        db_index=True
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        db_index=True
    )
    text = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)
    
    # Reply count for nested comment display
    replies_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'comments'
        indexes = [
            models.Index(fields=['post', 'parent', 'created_at'], name='comment_post_parent'),
            models.Index(fields=['user', 'created_at'], name='comment_user_created'),
            models.Index(fields=['deleted_at'], name='comment_deleted'),
            models.Index(fields=['post', 'deleted_at', 'created_at'], name='comment_post_deleted'),
        ]
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment by {self.user.username} on {self.post.id}"


class ReactionType(models.TextChoices):
    LIKE = 'like', _('Like')
    LOVE = 'love', _('Love')
    HAPPY = 'happy', _('Happy')
    ANGRY = 'angry', _('Angry')
    SAD = 'sad', _('Sad')
    WOW = 'wow', _('Wow')


class Reaction(models.Model):
    """
    Reaction model for multiple reaction types.
    One reaction per user per post.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='reactions',
        db_index=True
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reactions',
        db_index=True
    )
    type = models.CharField(
        max_length=10,
        choices=ReactionType.choices,
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'reactions'
        unique_together = ['post', 'user']
        indexes = [
            models.Index(fields=['post', 'type', 'created_at'], name='idx_reaction_post_type_created'),
            models.Index(fields=['user', 'type', 'created_at'], name='idx_reaction_user_type_created'),
            models.Index(fields=['type', 'created_at'], name='idx_reaction_type_created'),
        ]
    
    def __str__(self):
        return f"{self.user.username} {self.type}s {self.post.id}"


class MediaType(models.TextChoices):
    IMAGE = 'image', _('Image')
    VIDEO = 'video', _('Video')
    AUDIO = 'audio', _('Audio')


class MediaAsset(models.Model):
    """
    Media asset model for post attachments.
    Supports multiple file types with metadata.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='media_assets',
        db_index=True
    )
    file_type = models.CharField(
        max_length=10,
        choices=MediaType.choices,
        db_index=True
    )
    url = models.URLField(max_length=500)
    file_size = models.PositiveIntegerField()
    width = models.PositiveIntegerField(null=True, blank=True)
    height = models.PositiveIntegerField(null=True, blank=True)
    duration = models.PositiveIntegerField(null=True, blank=True)  # For video/audio in seconds
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'media_assets'
        indexes = [
            models.Index(fields=['post', 'file_type'], name='idx_media_post_type'),
            models.Index(fields=['file_type', 'created_at'], name='idx_media_type_created'),
        ]
    
    def __str__(self):
        return f"{self.file_type} for post {self.post.id}"
