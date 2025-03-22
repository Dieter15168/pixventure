from memberships.utils import check_if_user_is_paying
from media.models import MediaItem, MediaItemVersion

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

    # 3. Get the correct MediaItemVersion
    version_type = MediaItemVersion.WATERMARKED if not thumbnail else MediaItemVersion.THUMBNAIL
    version_query = media_item.versions.filter(version_type=version_type).first()

    if not version_query:
        return ""  # No matching version found, return empty string

    # 4. Separate logic if this is a PHOTO or VIDEO
    if media_item.media_type == MediaItem.PHOTO:
        # --- PHOTO LOGIC (supports blurred files) ---
        if user_is_paying:
            # Paying users see watermarked_file or thumbnail_file
            if thumbnail:
                return version_query.file.url if version_query.file else ""
            else:
                # Paying users always see the watermarked version
                return version_query.file.url if version_query.file else ""
        else:
            # Non-paying user
            if is_blurred:
                # Return blurred version
                if thumbnail:
                    # Non-paying user sees blurred thumbnail if available
                    blurred_version = media_item.versions.filter(version_type=MediaItemVersion.BLURRED_THUMBNAIL).first()
                    return blurred_version.file.url if blurred_version else ""
                else:
                    # Non-paying user sees blurred preview if available
                    blurred_version = media_item.versions.filter(version_type=MediaItemVersion.BLURRED_PREVIEW).first()
                    return blurred_version.file.url if blurred_version else ""
            else:
                # Return normal preview
                if thumbnail:
                    return version_query.file.url if version_query.file else ""
                else:
                    # Non-paying user sees preview file
                    preview_version = media_item.versions.filter(version_type=MediaItemVersion.PREVIEW).first()
                    return preview_version.file.url if preview_version else ""
    else:
        # --- VIDEO LOGIC (no blurred files exist) ---
        # If blurred => paying user sees watermarked, non-paying sees preview
        if user_is_paying:
            # Always see watermarked_file for paying users
            if thumbnail:
                # The thumbnail for a video is not blurred, so we use normal thumbnail_file if any
                thumbnail_version = media_item.versions.filter(version_type=MediaItemVersion.THUMBNAIL).first()
                return thumbnail_version.file.url if thumbnail_version else ""
            else:
                return version_query.file.url if version_query.file else ""
        else:
            # Non-paying user
            if thumbnail:
                return version_query.file.url if version_query.file else ""
            else:
                # Non-paying user sees preview for video
                preview_version = media_item.versions.filter(version_type=MediaItemVersion.PREVIEW).first()
                return preview_version.file.url if preview_version else ""

def is_media_locked(media_item, user, post=None):
    """
    Determines whether a media item should be considered 'locked' for the given user.
    Content is locked when:
      - The media is a photo
      - The user is not paying
      - Either the post or the media item is marked as blurred

    Args:
        media_item (MediaItem): The media item object.
        user (User): The user object.
        post (Post, optional): The post object that may indicate blurred status.

    Returns:
        bool: True if the media content is locked (i.e., a blurred version is served), False otherwise.
    """
    user_is_paying = check_if_user_is_paying(user)
    if media_item.media_type == MediaItem.PHOTO:
        post_blurred = getattr(post, 'is_blurred', False)
        return (not user_is_paying) and (post_blurred or media_item.is_blurred)
    # Videos are never blurred; thus, not locked.
    return False