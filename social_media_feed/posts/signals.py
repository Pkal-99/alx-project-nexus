from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import F, Count
from .models import Post, Follow, Comment, Reaction, MediaAsset


@receiver(post_save, sender=Post)
def update_post_count_on_create(sender, instance, created, **kwargs):
    """Update user's posts count when a post is created."""
    if created and instance.status == Post.PostStatus.PUBLISHED:
        from profiles.models import Profile
        Profile.objects.filter(user=instance.user).update(
            posts_count=F('posts_count') + 1
        )


@receiver(post_save, sender=Follow)
def update_follow_counts_on_create(sender, instance, created, **kwargs):
    """Update follower/following counts when a new follow relationship is created."""
    if created:
        from profiles.models import Profile
        
        # Update following count for follower
        Profile.objects.filter(user=instance.follower).update(
            following_count=F('following_count') + 1
        )
        
        # Update followers count for following user
        Profile.objects.filter(user=instance.following).update(
            followers_count=F('followers_count') + 1
        )


@receiver(post_delete, sender=Follow)
def update_follow_counts_on_delete(sender, instance, **kwargs):
    """Update follower/following counts when a follow relationship is deleted."""
    from profiles.models import Profile
    
    # Update following count for follower
    Profile.objects.filter(user=instance.follower).update(
        following_count=F('following_count') - 1
    )
    
    # Update followers count for following user
    Profile.objects.filter(user=instance.following).update(
        followers_count=F('followers_count') - 1
    )


@receiver(post_save, sender=Reaction)
def update_likes_count_on_create(sender, instance, created, **kwargs):
    """Update post's likes count when a reaction is created."""
    if created:
        Post.objects.filter(id=instance.post.id).update(
            likes_count=F('likes_count') + 1
        )


@receiver(post_delete, sender=Reaction)
def update_likes_count_on_delete(sender, instance, **kwargs):
    """Update post's likes count when a reaction is deleted."""
    Post.objects.filter(id=instance.post.id).update(
        likes_count=F('likes_count') - 1
    )


@receiver(post_save, sender=Comment)
def update_comments_count_on_create(sender, instance, created, **kwargs):
    """Update post's comments count when a comment is created."""
    if created and not instance.deleted_at:
        Post.objects.filter(id=instance.post.id).update(
            comments_count=F('comments_count') + 1
        )
        
        # Update parent comment's replies count if it's a reply
        if instance.parent:
            Comment.objects.filter(id=instance.parent.id).update(
                replies_count=F('replies_count') + 1
            )


@receiver(post_delete, sender=Comment)
def update_comments_count_on_delete(sender, instance, **kwargs):
    """Update post's comments count when a comment is deleted."""
    if not instance.deleted_at:
        Post.objects.filter(id=instance.post.id).update(
            comments_count=F('comments_count') - 1
        )
        
        # Update parent comment's replies count if it's a reply
        if instance.parent:
            Comment.objects.filter(id=instance.parent.id).update(
                replies_count=F('replies_count') - 1
            )
