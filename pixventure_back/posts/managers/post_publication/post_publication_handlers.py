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

    # If post is not approved and force is not set, we cannot publish.
    if post.status != Post.APPROVED and not force:
        logger.error(f"Post {post_id} is not approved (current: {post.get_status_display()}).")
        return False

    media_links = post.post_media_links.all().select_related("media_item")
    all_ok = True

    for link in media_links:
        item = link.media_item

        # 1) Ensure the item itself isn't stuck in moderation
        if item.status == MediaItem.PENDING_MODERATION:
            logger.error(f"MediaItem {item.id} in Post {post_id} is still in moderation.")
            all_ok = False
            continue  # No need to check further for this item

        # 2) Figure out what versions we require
        if item.media_type == MediaItem.PHOTO:
            # Photos require preview and watermarked.
            required_versions = {
                MediaItemVersion.PREVIEW,
                MediaItemVersion.WATERMARKED
            }
            # If the post or item is blurred, add blurred versions as well.
            if post.is_blurred or item.is_blurred:
                required_versions.update({
                    MediaItemVersion.BLURRED_THUMBNAIL,
                    MediaItemVersion.BLURRED_PREVIEW
                })
        else:
            # For videos, we only require PREVIEW and WATERMARKED.
            required_versions = {
                MediaItemVersion.PREVIEW,
                MediaItemVersion.WATERMARKED
            }

        # 3) Collect what versions the item actually has
        item_versions = set(
            item.versions.values_list("version_type", flat=True)
        )

        # 4) Check for missing versions
        if not required_versions.issubset(item_versions):
            missing = required_versions - item_versions
            logger.error(
                f"MediaItem {item.id} in Post {post_id} is missing required versions: {missing}. "
                f"Needed: {required_versions}, found: {item_versions}"
            )
            all_ok = False

    if not all_ok:
        logger.error(
            f"Post {post_id} failed publication checks due to unmoderated items or missing versions."
        )
        return False

    # If we got here, all items have the required versions, so publish.
    with transaction.atomic():
        post.status = Post.PUBLISHED
        post.published = timezone.now()
        post.save()

        # Update media items to PUBLISHED as well, if they're currently approved.
        for link in media_links:
            item = link.media_item
            if item.status == MediaItem.APPROVED:
                item.status = MediaItem.PUBLISHED
                item.save()

    logger.info(f"Post {post_id} published successfully.")
    return True
