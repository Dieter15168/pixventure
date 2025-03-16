# posts/managers/post_publication_manager.py
import logging
from django.db import transaction
from posts.models import Post
from media.models import MediaItem, MediaItemVersion
from django.utils import timezone

logger = logging.getLogger(__name__)

class PostPublicationManager:
    """
    Manager to handle the publication of a Post.
    
    Publication is allowed only if:
      - The post itself is in an approved state.
      - None of the associated media items are still in moderation.
    
    When publishing:
      - Media items that are Approved are updated to Published.
      - Media items that are Rejected remain unchanged.
      - The post itself is marked as Published.
    """

    @staticmethod
    def publish_post(post_id, force=False):
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            logger.error(f"Post with ID {post_id} does not exist.")
            return False

        # Ensure the post is in the approved state (or override with force)
        if post.status != Post.APPROVED and not force:
            logger.error(f"Post {post_id} is not in approved status (current: {post.get_status_display()}).")
            return False

        # Retrieve all media items linked to this post
        media_links = post.post_media_links.all().select_related('media_item')
        all_ok = True

        for link in media_links:
            item = link.media_item

            # If any item is still in moderation, halt publication
            if item.status == MediaItem.PENDING_MODERATION:
                logger.error(f"MediaItem {item.id} in Post {post_id} is still in moderation.")
                all_ok = False
                continue

            # Check that the item has all required versions.
            # Determine required versions: if the post or the item is blurred, require blurred versions too.
            requires_blurred = post.is_blurred or item.is_blurred
            required_versions = {MediaItemVersion.PREVIEW, MediaItemVersion.WATERMARKED}
            if requires_blurred:
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

        # Update statuses in an atomic transaction:
        with transaction.atomic():
            post.status = Post.PUBLISHED
            post.published = timezone.now()
            post.save()
            for link in media_links:
                item = link.media_item
                if item.status == MediaItem.APPROVED:
                    item.status = MediaItem.PUBLISHED
                    item.save()
                # Rejected items remain unchanged.

        logger.info(f"Post {post_id} and its approved media items have been published successfully.")
        return True
