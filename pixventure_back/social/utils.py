from social.models import Like

def user_has_liked(user, post=None, media_item=None, album=None):
    """
    Returns True if the given user has liked the specified post or media_item.
    If both post and media_item are provided, the function filters for both.
    If neither is provided, it returns False.
    """
    if not user or not user.is_authenticated:
        return False

    like_qs = Like.objects.filter(user=user)
    if post:
        like_qs = like_qs.filter(post=post)
    if media_item:
        like_qs = like_qs.filter(media_item=media_item)
    if album:
        like_qs = like_qs.filter(album=album)

    return like_qs.exists()