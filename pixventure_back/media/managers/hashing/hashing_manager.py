# media/managers/hashing_manager.py
from media.jobs.dispatcher import dispatch_fuzzy_hash
from media.models import MediaItemVersion, MediaItem

class HashingManager:
    """
    Manager to handle computing and storing fuzzy hashes for media item versions.
    """
    @staticmethod
    def process_fuzzy_hash(media_item_version_id, hash_type="phash"):
        try:
            version = MediaItemVersion.objects.get(id=media_item_version_id)
        except MediaItemVersion.DoesNotExist:
            raise ValueError(f"MediaItemVersion with ID {media_item_version_id} does not exist.")
        
        # Only process if the media item is an image.
        if version.media_item.media_type != MediaItem.PHOTO:
            return None
        
        # Dispatch the fuzzy hash task and don't wait for a result.
        dispatch_fuzzy_hash(media_item_version_id, hash_type, regenerate=False).apply_async(ignore_result=True)
        return None
