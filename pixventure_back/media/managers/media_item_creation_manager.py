# media/managers/media_item_creation_manager.py
import random
from media.models import MediaItem, MediaItemVersion
from media.services.file_processor import process_uploaded_file
from media.jobs.dispatcher import TaskDispatcher
from main.providers.settings_provider import SettingsProvider

class MediaItemCreationManager:
    """
    Manager for creating a MediaItem from an uploaded file.
    
    Workflow:
      1. Retrieve the item blur probability.
      2. Flip a coin to determine the `is_blurred` property.
      3. Create the media item using the file processor.
      4. Update the media item's `is_blurred` flag.
      5. Enqueue creation of media versions based on the blur flag.
      6. Enqueue a task to compute the phash for the original version.
    """
    
    @staticmethod
    def create_media_item(file_obj, user):
        # 1. Fetch the item blur probability (as a float between 0 and 1)
        prob_str = SettingsProvider.get_setting("item_blur_probability")
        try:
            item_blur_probability = float(prob_str)
        except (TypeError, ValueError):
            item_blur_probability = 0.0  # Default to 0 if not set

        # 2. Flip a coin to decide if the item is blurred.
        is_blurred = random.random() < item_blur_probability

        # 3. Process the file and create the media item.
        result = process_uploaded_file(file_obj, user)
        if "error" in result:
            return result

        media_item_id = result.get("media_item_id")
        # 4. Update the media item's is_blurred property.
        MediaItem.objects.filter(id=media_item_id).update(is_blurred=is_blurred)

        # 5. Enqueue media version creation.
        if is_blurred:
            allowed_versions = [
                # Create preview and full watermarked versions plus blurred versions.
                # (Assume constants like MediaItemVersion.PREVIEW, etc.)
                MediaItemVersion.PREVIEW,
                MediaItemVersion.WATERMARKED,
                MediaItemVersion.BLURRED_THUMBNAIL,
                MediaItemVersion.BLURRED_PREVIEW,
            ]
        else:
            allowed_versions = [
                MediaItemVersion.PREVIEW,
                MediaItemVersion.WATERMARKED,
            ]
        TaskDispatcher.dispatch_media_item_versions(
            media_item_id,
            regenerate=False,
            allowed_versions=allowed_versions
        )
        
        # 6. Enqueue phash computation for the original version.
        # Assumes that the original version was created in process_uploaded_file.
        # Retrieve the original version and dispatch the fuzzy hash task.
        try:
            media_item = MediaItem.objects.get(id=media_item_id)
            original_version = media_item.versions.get(version_type=MediaItemVersion.ORIGINAL)
            TaskDispatcher.dispatch_fuzzy_hash(media_item_version_id=original_version.id, hash_type="phash")
        except Exception as e:
            # Log error if necessary; phash computation failure shouldn't block item creation.
            pass

        return result
