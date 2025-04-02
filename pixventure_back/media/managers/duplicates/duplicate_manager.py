# media/managers/duplicate_manager.py
import logging
from media.models import MediaItemVersion, MediaItemHash, DuplicateCase

logger = logging.getLogger(__name__)

class DuplicateManager:
    """
    Manager to handle duplicate detection based on fuzzy hash comparisons.
    Creates individual DuplicateCase records for each candidate-duplicate pair.
    """
    @staticmethod
    def process_duplicates(media_item_version_id, hash_value, hash_type="phash"):
        try:
            version = MediaItemVersion.objects.get(id=media_item_version_id)
        except MediaItemVersion.DoesNotExist:
            logger.error("MediaItemVersion with ID %s does not exist.", media_item_version_id)
            return []
        
        candidate_media_item = version.media_item
        duplicate_cases_created = []
        
        # Find matching hashes (exclude the current version)
        duplicate_hashes = MediaItemHash.objects.filter(
            hash_type__name=hash_type,
            hash_value=hash_value
        ).exclude(media_item_version=version)
        
        for dup_hash in duplicate_hashes:
            duplicate_media_item = dup_hash.media_item_version.media_item
            # For an exact match, set confidence_score = 1.0. In future, use a proper function.
            duplicate_case = DuplicateCase.objects.create(
                candidate=candidate_media_item,
                duplicate=duplicate_media_item,
                confidence_score=1.0,
                status=DuplicateCase.PENDING
            )
            duplicate_cases_created.append(duplicate_case)
            logger.info("Created DuplicateCase: Candidate %s vs Duplicate %s", candidate_media_item.id, duplicate_media_item.id)
        
        if not duplicate_cases_created:
            logger.info("No duplicates found for MediaItemVersion %s", media_item_version_id)
        return duplicate_cases_created
