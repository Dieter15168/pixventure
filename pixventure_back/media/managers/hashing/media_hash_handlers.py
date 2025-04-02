# media/managers/media_hash_handlers.py
import logging
from media.models import MediaItemVersion, MediaItemHash, HashType
from media.services.hasher import compute_fuzzy_hash

logger = logging.getLogger(__name__)

def handle_fuzzy_hash(media_item_version_id, config, regenerate=False, hash_type="phash"):
    """
    Computes the fuzzy hash for a MediaItemVersion and stores it.
    
    :param media_item_version_id: ID of the MediaItemVersion.
    :param config: Configuration dictionary (not used in this simple handler, but provided for consistency).
    :param regenerate: Boolean flag (ignored here).
    :param hash_type: Type of hash to compute, defaults to "phash".
    :return: Return a context dictionary with all necessary data.
    """
    try:
        version = MediaItemVersion.objects.get(id=media_item_version_id)
    except MediaItemVersion.DoesNotExist:
        raise ValueError(f"MediaItemVersion with ID {media_item_version_id} does not exist.")
    
    file_obj = version.file
    hash_value = compute_fuzzy_hash(file_obj, hash_type=hash_type)
    
    hash_type_obj, _ = HashType.objects.get_or_create(name=hash_type)
    MediaItemHash.objects.update_or_create(
        media_item_version=version,
        hash_type=hash_type_obj,
        defaults={"hash_value": hash_value}
    )
    
    logger.info("Computed fuzzy hash for MediaItemVersion %s", media_item_version_id)
    
    return {
        "media_item_version_id": media_item_version_id,
        "hash_value": hash_value,
        "hash_type": hash_type,
    }

