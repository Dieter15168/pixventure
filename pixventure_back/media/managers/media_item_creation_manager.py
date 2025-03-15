# media/managers/media_item_creation_manager.py
import random
from django.db import transaction
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
      5. Enqueue creation of media versions:
            - If not blurred: only preview and full watermarked versions.
            - If blurred: also enqueue blurred thumbnail and blurred preview.
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
        return result
