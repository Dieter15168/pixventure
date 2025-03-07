# social/utils.py
from django.db import transaction
from django.conf import settings
from .models import Like
from django.contrib.auth import get_user_model

def user_has_liked(user, post=None, media_item=None, album=None, liked_user=None):
    """
    Returns True if the given user (liking_user) has an active like for the specified target.
    """
    if not user or not user.is_authenticated:
        return False

    like_qs = Like.objects.filter(liking_user=user, is_active=True)
    if post:
        like_qs = like_qs.filter(post=post)
    if media_item:
        like_qs = like_qs.filter(media_item=media_item)
    if album:
        like_qs = like_qs.filter(album=album)
    if liked_user:
        like_qs = like_qs.filter(liked_user=liked_user)

    return like_qs.exists()

@transaction.atomic
def toggle_like(user, target_type, target_id, like=True):
    """
    Toggles a like for the specified target.
    
    If like=True:
      - Creates a new Like (or re-activates an existing inactive Like) and increments the target's likes_counter.
    If like=False:
      - Deactivates an active Like (if one exists) and decrements the target's likes_counter.
      
    target_type can be: "post", "media", "album", "user".
    
    If the target object does not exist, it raises a ValueError.
    Detailed error messages are returned only if settings.DEBUG is True.
    """
    if not user.is_authenticated:
        raise ValueError("User must be authenticated")

    target_obj = None
    try:
        if target_type == 'post':
            from posts.models import Post
            target_obj = Post.objects.get(id=target_id)
        elif target_type == 'media':
            from media.models import MediaItem
            target_obj = MediaItem.objects.get(id=target_id)
        elif target_type == 'album':
            from albums.models import Album
            target_obj = Album.objects.get(id=target_id)
        elif target_type == 'user':
            # Now we use the default User model for liking a user.
            User = get_user_model()
            target_obj = User.objects.get(id=target_id)
        else:
            raise ValueError("Invalid target_type")
    except Exception as e:
        if settings.DEBUG:
            raise ValueError(f"Target object error: {e}")
        else:
            raise ValueError("Target object not found")

    # Find or create the Like object.
    like_obj, created = Like.objects.get_or_create(
        liking_user=user,
        post=target_obj if target_type == 'post' else None,
        media_item=target_obj if target_type == 'media' else None,
        album=target_obj if target_type == 'album' else None,
        liked_user=target_obj if target_type == 'user' else None,
        defaults={'is_active': True}
    )

    if like:
        if created or not like_obj.is_active:
            like_obj.is_active = True
            like_obj.save()
            increment_likes_counter(target_obj)
    else:
        if like_obj.is_active:
            like_obj.is_active = False
            like_obj.save()
            decrement_likes_counter(target_obj)

def increment_likes_counter(target_obj):
    target_obj.likes_counter += 1
    target_obj.save(update_fields=['likes_counter'])

def decrement_likes_counter(target_obj):
    if target_obj.likes_counter > 0:
        target_obj.likes_counter -= 1
        target_obj.save(update_fields=['likes_counter'])
