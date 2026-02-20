from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Notification


@receiver(post_save, sender='posts.Follow')
def create_follow_notification(sender, instance, created, **kwargs):
    """Create notification when someone follows a user."""
    if created:
        Notification.objects.create(
            recipient=instance.following,
            actor=instance.follower,
            notification_type=Notification.NotificationType.FOLLOW,
            title=f"New Follower",
            message=f"{instance.follower.username} started following you",
        )


@receiver(post_save, sender='posts.Comment')
def create_comment_notification(sender, instance, created, **kwargs):
    """Create notification when someone comments on a post."""
    if created and not instance.deleted_at:
        # Don't notify if user comments on their own post
        if instance.post.user != instance.user:
            Notification.objects.create(
                recipient=instance.post.user,
                actor=instance.user,
                post=instance.post,
                comment=instance,
                notification_type=Notification.NotificationType.COMMENT,
                title=f"New Comment",
                message=f"{instance.user.username} commented on your post",
            )


@receiver(post_save, sender='posts.Reaction')
def create_reaction_notification(sender, instance, created, **kwargs):
    """Create notification when someone reacts to a post."""
    if created:
        # Don't notify if user reacts to their own post
        if instance.post.user != instance.user:
            Notification.objects.create(
                recipient=instance.post.user,
                actor=instance.user,
                post=instance.post,
                reaction=instance,
                notification_type=Notification.NotificationType.REACTION,
                title=f"New {instance.get_type_display()}",
                message=f"{instance.user.username} {instance.type}d your post",
            )
