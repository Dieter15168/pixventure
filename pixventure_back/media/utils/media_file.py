from memberships.utils import check_if_user_is_paying
from media.models import MediaItem, MediaItemVersion


def get_media_display_info(media_item, user, post=None, thumbnail=False):
    """
    Returns a tuple of (chosen_version, chosen_url) for a MediaItem:
      - chosen_version: the MediaItemVersion instance used.
      - chosen_url: the corresponding file URL string.

    This function encapsulates all the logic of picking which version is served
    (blurred preview, watermarked, etc.), so we only have to maintain it in one place.

    Then get_media_file_for_display() can simply call this function and return
    only the URL, for backward compatibility.
    """
    # (1) Get the final URL from your existing logic
    #     We'll call the existing function. 
    #     But we also need to figure out which version was chosen.
    #
    #     Because your existing function only returns the URL, we need to replicate
    #     enough of its logic to determine the chosen_version. If you prefer to keep
    #     your existing function 100% untouched, you can do so, but you'd have to
    #     replicate the logic here. Instead, we can shift the actual logic from
    #     get_media_file_for_display() into this new function, then have the old
    #     function call *this* to get the URL. 
    #
    # For illustration, let's move the entire logic from get_media_file_for_display here,
    # so we can also track the chosen_version in parallel:

    user_is_paying = check_if_user_is_paying(user)
    post_blurred = getattr(post, 'is_blurred', False) if post else False
    item_blurred = media_item.is_blurred
    is_blurred = post_blurred or item_blurred

    chosen_version = None
    chosen_url = ""

    if media_item.media_type == MediaItem.VIDEO:
        # -- VIDEO --
        # Watermarked or thumbnail version_type
        version_type = (MediaItemVersion.THUMBNAIL if thumbnail
                        else MediaItemVersion.WATERMARKED)
        version_obj = media_item.versions.filter(version_type=version_type).first()
        if user_is_paying:
            # paying user sees watermarked or thumbnail
            if version_obj and version_obj.file:
                chosen_version = version_obj
                chosen_url = version_obj.file.url
            else:
                chosen_version = None
                chosen_url = ""
        else:
            # non-paying sees preview or thumbnail
            if thumbnail:
                if version_obj and version_obj.file:
                    chosen_version = version_obj
                    chosen_url = version_obj.file.url
            else:
                preview_obj = media_item.versions.filter(version_type=MediaItemVersion.PREVIEW).first()
                if preview_obj and preview_obj.file:
                    chosen_version = preview_obj
                    chosen_url = preview_obj.file.url

    else:
        # -- PHOTO --
        # If user is paying => watermarked/thumbnail
        # If not => blurred or preview
        if user_is_paying:
            # For paying users, we use watermarked or thumbnail
            version_type = (MediaItemVersion.THUMBNAIL if thumbnail
                            else MediaItemVersion.WATERMARKED)
            version_obj = media_item.versions.filter(version_type=version_type).first()
            if version_obj and version_obj.file:
                chosen_version = version_obj
                chosen_url = version_obj.file.url

        else:
            # Non-paying user
            if is_blurred:
                # blurred thumbnail or blurred preview
                version_type = (MediaItemVersion.BLURRED_THUMBNAIL if thumbnail
                                else MediaItemVersion.BLURRED_PREVIEW)
                version_obj = media_item.versions.filter(version_type=version_type).first()
                if version_obj and version_obj.file:
                    chosen_version = version_obj
                    chosen_url = version_obj.file.url
            else:
                # normal thumbnail or normal preview
                if thumbnail:
                    # normal thumbnail
                    version_obj = media_item.versions.filter(version_type=MediaItemVersion.THUMBNAIL).first()
                    if version_obj and version_obj.file:
                        chosen_version = version_obj
                        chosen_url = version_obj.file.url
                else:
                    # normal preview
                    preview_obj = media_item.versions.filter(version_type=MediaItemVersion.PREVIEW).first()
                    if preview_obj and preview_obj.file:
                        chosen_version = preview_obj
                        chosen_url = preview_obj.file.url

    # If no version found or no file, fallback to empty strings
    if not chosen_version:
        chosen_version = None
        chosen_url = ""

    return chosen_version, chosen_url


def get_media_file_for_display(media_item, user, post=None, thumbnail=False):
    """
    Preserves the old signature, but re-uses the new logic:
    """
    _, chosen_url = get_media_display_info(media_item, user, post, thumbnail)
    return chosen_url


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