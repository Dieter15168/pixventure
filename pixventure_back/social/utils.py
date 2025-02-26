# social/utils.py
from django.db import transaction
from .models import Like
from django.contrib.auth.models import User

def user_has_liked(user, post=None, media_item=None, album=None, user_profile=None):
    """
    Returns True if the given user has an active (is_active=True) like
    for the specified target (post, media_item, album, or user_profile).
    """
    if not user or not user.is_authenticated:
        return False

    like_qs = Like.objects.filter(user=user, is_active=True)  # only active likes
    if post:
        like_qs = like_qs.filter(post=post)
    if media_item:
        like_qs = like_qs.filter(media_item=media_item)
    if album:
        like_qs = like_qs.filter(album=album)
    if user_profile:
        like_qs = like_qs.filter(user_profile=user_profile)

    return like_qs.exists()


@transaction.atomic
def toggle_like(user, target_type, target_id, like=True):
    """
    If like=True, we attempt to make or re-activate a like on the target.
    If like=False, we set the like to inactive.
    
    target_type can be "post", "media", "album", "user_profile".
    """
    if not user.is_authenticated:
        raise ValueError("User must be authenticated")
    
    # 1. Identify the target model & object
    target_obj = None
    if target_type == 'post':
        from posts.models import Post
        target_obj = Post.objects.get(id=target_id)
    elif target_type == 'media':
        from media.models import MediaItem
        target_obj = MediaItem.objects.get(id=target_id)
    elif target_type == 'album':
        from albums.models import Album
        target_obj = Album.objects.get(id=target_id)
    elif target_type == 'user_profile':
        from accounts.models import UserProfile
        target_obj = UserProfile.objects.get(id=target_id)
    else:
        raise ValueError("Invalid target_type")

    # 2. Find or create the Like
    like_obj, created = Like.objects.get_or_create(
        user=user,
        post=target_obj if target_type=='post' else None,
        media_item=target_obj if target_type=='media' else None,
        album=target_obj if target_type=='album' else None,
        user_profile=target_obj if target_type=='user_profile' else None,
        defaults={'is_active': True}
    )

    # 3. If we want to "like"
    if like:
        # If it was previously inactive, re-activate it and increment
        if not like_obj.is_active:
            like_obj.is_active = True
            like_obj.save()
            # increment the target's likes_counter
            increment_likes_counter(target_obj)
    else:
        # If we want to "unlike"
        if like_obj.is_active:
            like_obj.is_active = False
            like_obj.save()
            # decrement the target's likes_counter
            decrement_likes_counter(target_obj)

def increment_likes_counter(target_obj):
    target_obj.likes_counter += 1
    target_obj.save(update_fields=['likes_counter'])

def decrement_likes_counter(target_obj):
    if target_obj.likes_counter > 0:
        target_obj.likes_counter -= 1
        target_obj.save(update_fields=['likes_counter'])