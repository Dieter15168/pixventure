# media/managers/duplicate_manager.py
import logging
from media.models import (
    MediaItemVersion,
    MediaItemHash,
    DuplicateCluster,
    HashType
)

logger = logging.getLogger(__name__)

class DuplicateManager:
    """
    Manager that handles grouping items with the same fuzzy hash into a DuplicateCluster.
    """

    @staticmethod
    def process_duplicates(media_item_version_id, hash_value, hash_type="phash"):
        try:
            version = MediaItemVersion.objects.get(id=media_item_version_id)
        except MediaItemVersion.DoesNotExist:
            logger.error("MediaItemVersion with ID %s does not exist.", media_item_version_id)
            return None

        candidate_media_item = version.media_item

        # Try to get or create a cluster for this hash_type + hash_value.
        # If your logic is to keep them all in one cluster, we do this:
        try:
            hash_type_obj = HashType.objects.get(name=hash_type)
        except HashType.DoesNotExist:
            logger.error("HashType '%s' does not exist.", hash_type)
            return None

        cluster, created = DuplicateCluster.objects.get_or_create(
            hash_type=hash_type_obj,
            hash_value=hash_value,
            defaults={"status": DuplicateCluster.PENDING}
        )

        # Add the candidate to the cluster
        cluster.items.add(candidate_media_item)

        # Also fetch all existing items that share the same hash (exclude current version).
        # We'll add them to the same cluster if they're not already.
        duplicate_hashes = MediaItemHash.objects.filter(
            hash_type__name=hash_type,
            hash_value=hash_value
        ).exclude(media_item_version=version)

        for dup_hash in duplicate_hashes:
            existing_duplicate_item = dup_hash.media_item_version.media_item
            cluster.items.add(existing_duplicate_item)

        # If you want to ensure the cluster remains in PENDING if not confirmed, do it here.
        if cluster.status != DuplicateCluster.CONFIRMED:
            cluster.status = DuplicateCluster.PENDING
        cluster.save()

        logger.info(
            "DuplicateCluster %s updated with new item %s (hash: %s).",
            cluster.id, candidate_media_item.id, hash_value
        )
        return cluster
