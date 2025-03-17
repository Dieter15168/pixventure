# posts/managers/post_publication_handlers.py
import logging
from django.db import transaction
from django.utils import timezone
from posts.models import Post
from media.models import MediaItem, MediaItemVersion

logger = logging.getLogger(__name__)

def handle_post_publication(post_id, config, regenerate=False):
    """
    Handler for post publication.
    
    Publication is allowed only if:
      - The post is in APPROVED status (or force override is used),
      - None of the associated media items are still in moderation,
      - All media items have the required versions.
    
    On success:
      - The post status is updated to PUBLISHED (and the published timestamp is set),
      - Approved media items are updated to PUBLISHED.
    
    :param post_id: The ID of the post to publish.
    :param config: A configuration dict that must contain a boolean "force" flag.
    :param regenerate: (Not used here, but present for consistency)
    :return: True on success, False otherwise.
    """
    force = config.get("force", False)
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        logger.error(f"Post with ID {post_id} does not exist.")
        return False

    if post.status != Post.APPROVED and not force:
        logger.error(f"Post {post_id} is not approved (current: {post.get_status_display()}).")
        return False

    media_links = post.post_media_links.all().select_related('media_item')
    all_ok = True
    for link in media_links:
        item = link.media_item
        if item.status == MediaItem.PENDING_MODERATION:
            logger.error(f"MediaItem {item.id} in Post {post_id} is still in moderation.")
            all_ok = False
        else:
            # Determine required versions: always require PREVIEW and WATERMARKED.
            required_versions = {MediaItemVersion.PREVIEW, MediaItemVersion.WATERMARKED}
            if post.is_blurred or item.is_blurred:
                required_versions |= {MediaItemVersion.BLURRED_THUMBNAIL, MediaItemVersion.BLURRED_PREVIEW}
            item_versions = set(item.versions.values_list("version_type", flat=True))
            if not required_versions.issubset(item_versions):
                logger.error(
                    f"MediaItem {item.id} in Post {post_id} is missing required versions. "
                    f"Expected: {required_versions}, found: {item_versions}"
                )
                all_ok = False

    if not all_ok:
        logger.error(f"Post {post_id} failed publication checks due to unmoderated items or missing versions.")
        return False

    with transaction.atomic():
        post.status = Post.PUBLISHED
        post.published = timezone.now()
        post.save()
        for link in media_links:
            item = link.media_item
            if item.status == MediaItem.APPROVED:
                item.status = MediaItem.PUBLISHED
                item.save()

    logger.info(f"Post {post_id} published successfully.")
    return True
