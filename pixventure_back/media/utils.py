from memberships.utils import check_if_user_is_paying

from memberships.utils import check_if_user_is_paying
from media.models import MediaItem

def get_media_file_for_display(media_item, user, post=None, thumbnail=False):
    """
    Returns the appropriate file URL for a MediaItem given:
      - user's membership status
      - whether post or item is blurred
      - whether we want thumbnail or "full" file

    Special logic for videos:
      - Videos do not have blurred versions (blurred_thumbnail_file, blurred_preview_file).
        If the video or post is blurred:
           - paying users see watermarked_file
           - non-paying users see preview_file
           - thumbnail is always the normal thumbnail_file (if any)

    Photos:
      - If user is paying => always watermarked_file (or thumbnail_file if thumbnail=True)
        ignoring blur
      - If user is non-paying:
          * If blurred => use blurred_preview_file or blurred_thumbnail_file
          * If not blurred => use preview_file or thumbnail_file
    """

    # 1. Check if user is paying
    user_is_paying = check_if_user_is_paying(user)

    # 2. Determine if the content is blurred
    #    If the post is blurred OR the item is blurred => entire content is blurred
    post_blurred = getattr(post, 'is_blurred', False)  # post may be None if unknown
    item_blurred = media_item.is_blurred
    is_blurred = (post_blurred or item_blurred)

    # 3. Separate logic if this is a PHOTO or VIDEO
    if media_item.item_type == MediaItem.PHOTO:
        # --- PHOTO LOGIC (supports blurred files) ---
        if user_is_paying:
            # Paying users see watermarked_file or thumbnail_file
            if thumbnail:
                return media_item.thumbnail_file.url if media_item.thumbnail_file else ""
            else:
                return media_item.watermarked_file.url if media_item.watermarked_file else ""
        else:
            # Non-paying user
            if is_blurred:
                # Return blurred version
                if thumbnail:
                    return media_item.blurred_thumbnail_file.url if media_item.blurred_thumbnail_file else ""
                else:
                    return media_item.blurred_preview_file.url if media_item.blurred_preview_file else ""
            else:
                # Return normal preview
                if thumbnail:
                    return media_item.thumbnail_file.url if media_item.thumbnail_file else ""
                else:
                    return media_item.preview_file.url if media_item.preview_file else ""
    else:
        # --- VIDEO LOGIC (no blurred files exist) ---
        # If blurred => paying user sees watermarked, non-paying sees preview
        if user_is_paying:
            # Always see watermarked_file for paying users
            if thumbnail:
                # The thumbnail for a video is not blurred, so we use normal thumbnail_file if any
                return media_item.thumbnail_file.url if media_item.thumbnail_file else ""
            else:
                return media_item.watermarked_file.url if media_item.watermarked_file else ""
        else:
            # Non-paying user
            # Even if blurred, we do not have a "blurred" version, so we still serve preview_file
            if thumbnail:
                return media_item.thumbnail_file.url if media_item.thumbnail_file else ""
            else:
                return media_item.preview_file.url if media_item.preview_file else ""
