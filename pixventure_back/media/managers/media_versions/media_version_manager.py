# media/managers/media_version_manager.py
import logging
from media.models import MediaItem
from main.providers.settings_provider import SettingsProvider
from media.managers.media_versions import media_version_determiner, media_version_scheduler

logger = logging.getLogger(__name__)

class MediaVersionManager:
    """
    Central manager to create additional media item versions.
    
    This class delegates:
      (1) Determining required versions,
      (2) Scheduling tasks (with separate logic for images vs. videos).
    """
    def __init__(self, media_item_id: int):
        self.media_item_id = media_item_id
        try:
            self.media_item = MediaItem.objects.get(id=media_item_id)
        except MediaItem.DoesNotExist:
            raise ValueError(f"MediaItem with ID {media_item_id} does not exist.")
        # Load configuration settings.
        self.config = SettingsProvider.get_all_settings()

    def process_versions(self, regenerate: bool = False, allowed_versions: list = None):
        """
        High-level method to process versions for the media item.
        If allowed_versions is not provided, it is determined automatically.
        """
        if allowed_versions is None:
            allowed_versions = media_version_determiner.determine_allowed_versions(self.media_item)
        # Delegate scheduling based on media type.
        media_version_scheduler.schedule_versions(self.media_item, self.config, allowed_versions, regenerate)
