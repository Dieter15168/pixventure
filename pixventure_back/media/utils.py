from memberships.utils import check_if_user_is_paying

def get_media_file_for_display(media_item, user, post=None, thumbnail=False):
    """
    Returns the appropriate file URL for a MediaItem given:
      - user's membership status
      - whether post or item is blurred
      - whether we want thumbnail or "full" file
    """

    # 1. Check if user is paying
    user_is_paying = check_if_user_is_paying(user)

    # 2. Determine if the content is blurred
    #    If the post is blurred OR the item is blurred => entire content is blurred
    post_blurred = getattr(post, 'is_blurred', False)  # post may be None if unknown
    item_blurred = media_item.is_blurred
    is_blurred = post_blurred or item_blurred

    # 3. Decide which field to use
    if user_is_paying:
        # Paying users see watermarked_file (full resolution) if not blurred
        # But if the item/post is blurred, do we still want to serve blurred content 
        # or do paying users see it unblurred? The business logic says:
        # "A paying user always sees non-blurred content"
        # so presumably we ignore the blur in that case:
        if thumbnail:
            return media_item.thumbnail_file.url if media_item.thumbnail_file else ""
        else:
            return media_item.watermarked_file.url if media_item.watermarked_file else ""
    else:
        # Non-paying user
        # If blurred => return blurred version 
        if is_blurred:
            if thumbnail:
                return media_item.blurred_thumbnail_file.url if media_item.blurred_thumbnail_file else ""
            else:
                return media_item.blurred_preview_file.url if media_item.blurred_preview_file else ""
        else:
            # Non-blurred => see normal preview 
            if thumbnail:
                return media_item.thumbnail_file.url if media_item.thumbnail_file else ""
            else:
                return media_item.preview_file.url if media_item.preview_file else ""
