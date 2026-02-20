import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from profiles.models import User


class NotificationType(models.TextChoices):
    FOLLOW = 'follow', _('Follow')
    COMMENT = 'comment', _('Comment')
    REACTION = 'reaction', _('Reaction')
    POST = 'post', _('Post')
    MENTION = 'mention', _('Mention')


class Notification(models.Model):
    """
    Notification model with polymorphic relationships.
    Supports multiple notification types with proper indexing.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        db_index=True
    )
    actor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_notifications',
        db_index=True
    )
    
    # Polymorphic relationships - can reference different objects
    post = models.ForeignKey(
        'posts.Post',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications',
        db_index=True
    )
    comment = models.ForeignKey(
        'posts.Comment',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications',
        db_index=True
    )
    reaction = models.ForeignKey(
        'posts.Reaction',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications',
        db_index=True
    )
    
    notification_type = models.CharField(
        max_length=20,
        choices=NotificationType.choices,
        db_index=True
    )
    
    # Notification content
    title = models.CharField(max_length=200)
    message = models.TextField(max_length=500)
    
    # Status tracking
    is_read = models.BooleanField(default=False, db_index=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'notifications'
        indexes = [
            models.Index(fields=['recipient', 'is_read', 'created_at'], name='notif_rec_read_created'),
            models.Index(fields=['actor', 'created_at'], name='notif_actor_created'),
            models.Index(fields=['notification_type', 'created_at'], name='notif_type_created'),
            models.Index(fields=['post', 'notification_type'], name='notif_post_type'),
            models.Index(fields=['comment', 'notification_type'], name='notif_comment_type'),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Notification for {self.recipient.username}: {self.title}"
