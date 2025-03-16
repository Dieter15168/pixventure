# media/managers/media_version_determiner.py
from media.models import MediaItem, MediaItemVersion

def determine_allowed_versions(media_item):
    """
    Returns a list of version type constants that should be generated for this media item.
    
    For videos:
      Always require WATERMARKED, PREVIEW, and THUMBNAIL.
    For images:
      Always require PREVIEW and WATERMARKED.
      If the item or its related post is blurred, also require BLURRED_THUMBNAIL and BLURRED_PREVIEW.
    """
    if media_item.media_type == MediaItem.VIDEO:
        return [MediaItemVersion.WATERMARKED, MediaItemVersion.PREVIEW, MediaItemVersion.THUMBNAIL]
    else:
        allowed = [MediaItemVersion.PREVIEW, MediaItemVersion.WATERMARKED]
        if media_item.is_blurred or (hasattr(media_item, 'post') and media_item.post.is_blurred):
            allowed.extend([MediaItemVersion.BLURRED_THUMBNAIL, MediaItemVersion.BLURRED_PREVIEW])
        return allowed
