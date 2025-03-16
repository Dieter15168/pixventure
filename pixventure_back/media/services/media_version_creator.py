# media/services/media_version_creator.py
import logging
from django.db import transaction
from media.models import MediaItem, MediaItemVersion, MediaItemHash, HashType
from media.services.hasher import compute_file_hash
from media.services.image_metadata import extract_image_metadata

logger = logging.getLogger(__name__)

def create_media_item_version(
    media_item: MediaItem,
    file_obj,
    version_type: int,
    hash_type_name: str = "blake3",
    existing_hash_value: str = None,
    is_image: bool = False
) -> MediaItemVersion:
    from media.services.video_metadata import extract_video_metadata  # if you have that
    with transaction.atomic():
        version = MediaItemVersion.objects.create(
            media_item=media_item,
            version_type=version_type,
            file=file_obj
        )
        logger.debug("create_media_item_version: Created version id=%s, is_image=%s", version.id, is_image)

        if is_image:
            try:
                meta = extract_image_metadata(file_obj)
                logger.debug("create_media_item_version: Image meta: %s", meta)
                version.width = meta["width"]
                version.height = meta["height"]
                version.file_size = meta["file_size"]
            except Exception as e:
                logger.error("create_media_item_version: Could not extract image metadata: %s", e)
                raise ValueError("Could not extract image metadata.")
        else:
            # Attempt video metadata extraction
            try:
                vmeta = extract_video_metadata(file_obj)
                logger.debug("create_media_item_version: Video meta: %s", vmeta)
                version.width = vmeta["width"]
                version.height = vmeta["height"]
                version.video_duration = vmeta["duration"]
                version.file_size = file_obj.size
            except Exception as e:
                logger.warning("create_media_item_version: Could not extract video metadata: %s", e)
                # fallback to file_size only
                version.file_size = file_obj.size

        version.save()

        if existing_hash_value:
            hash_value = existing_hash_value
        else:
            hash_value = compute_file_hash(file_obj, hash_type=hash_type_name)
        hash_type_obj, _ = HashType.objects.get_or_create(name=hash_type_name)
        MediaItemHash.objects.create(
            media_item_version=version,
            hash_type=hash_type_obj,
            hash_value=hash_value
        )

        logger.debug("create_media_item_version: Version id=%s finalized, returning it.", version.id)
    return version
