# media/managers/duplicates/duplicate_handlers.py

import logging
from media.managers.duplicates.duplicate_manager import DuplicateManager
from media.models import MediaItemVersion, HashType

logger = logging.getLogger(__name__)

def handle_duplicate_detection(input_data, config, regenerate):
    """
    Handler for duplicate detection.
    
    This function accepts either:
      - A context dictionary from a previous fuzzy hash task (containing media_item_version_id, hash_value, hash_type), or
      - A direct media_item_version_id.
    
    It retrieves the fuzzy hash (either from the context or from the database) and then
    invokes the DuplicateManager to process duplicate cases.
    """
    if isinstance(input_data, dict):
        context = input_data
        media_item_version_id = context.get("media_item_version_id")
        hash_value = context.get("hash_value")
        hash_type = context.get("hash_type", config.get("hash_type", "phash"))
    else:
        media_item_version_id = input_data
        hash_type = config.get("hash_type", "phash")
        # Retrieve hash value from DB if not provided in a context
        try:
            version = MediaItemVersion.objects.get(id=media_item_version_id)
            hash_type_obj, _ = HashType.objects.get_or_create(name=hash_type)
            media_hash = version.hashes.filter(hash_type=hash_type_obj).first()
            if not media_hash:
                raise ValueError(f"Fuzzy hash not found for MediaItemVersion {media_item_version_id}")
            hash_value = media_hash.hash_value
        except Exception as e:
            logger.error("Error retrieving fuzzy hash for MediaItemVersion %s: %s", media_item_version_id, e)
            raise e

    duplicate_cases = DuplicateManager.process_duplicates(media_item_version_id, hash_value, hash_type)
    logger.info(
        "Duplicate detection completed for MediaItemVersion %s: %d cases created",
        media_item_version_id, len(duplicate_cases)
    )
    return {"duplicate_cases_created": len(duplicate_cases)}
