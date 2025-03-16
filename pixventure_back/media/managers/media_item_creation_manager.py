# media/managers/media_item_creation_manager.py
import random
from media.models import MediaItem, MediaItemVersion
from media.services.file_processor import process_uploaded_file
from media.managers.media_versions.media_version_manager import MediaVersionManager
from media.managers.hashing.hashing_manager import HashingManager
from main.providers.settings_provider import SettingsProvider

class MediaItemCreationManager:
    """
    Manager for creating a MediaItem from an uploaded file.
    
    Workflow:
      1. Retrieve the item blur probability.
      2. Flip a coin to determine the `is_blurred` property.
      3. Create the media item using the file processor.
      4. Update the media item's `is_blurred` flag.
      5. Call the MediaVersionManager to process required media versions.
      6. Call the HashingManager to enqueue fuzzy hash computation for the original version.
    """
    
    @staticmethod
    def create_media_item(file_obj, user):
        # 1. Fetch the item blur probability.
        prob_str = SettingsProvider.get_setting("item_blur_probability")
        try:
            item_blur_probability = float(prob_str)
        except (TypeError, ValueError):
            item_blur_probability = 0.0  # Default
        
        # 2. Decide if the item should be blurred.
        is_blurred = random.random() < item_blur_probability
        
        # 3. Process the file and create the media item.
        result = process_uploaded_file(file_obj, user)
        if "error" in result:
            return result
        
        media_item_id = result.get("media_item_id")
        # 4. Update the media item's blur flag.
        MediaItem.objects.filter(id=media_item_id).update(is_blurred=is_blurred)
        
        # 5. Delegate version creation to the MediaVersionManager.
        mvm = MediaVersionManager(media_item_id)
        # The MediaVersionManager will determine which versions are needed based on the media item.
        mvm.process_versions(regenerate=False)
        
        # 6. Enqueue fuzzy hash computation via the HashingManager.
        try:
            media_item = MediaItem.objects.get(id=media_item_id)
            original_version = media_item.versions.get(version_type=MediaItemVersion.ORIGINAL)
            # This call dispatches the fuzzy hash task.
            HashingManager.process_fuzzy_hash(original_version.id, hash_type="phash")
        except Exception as e:
            # Log error if needed; fuzzy hash failure shouldn't block item creation.
            pass

        return result
