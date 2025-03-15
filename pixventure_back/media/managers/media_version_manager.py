# media/managers/media_version_manager.py
import logging
from media.models import MediaItem, MediaItemVersion
from media.services import media_version_creator, watermark
from media.services.settings_provider import MediaSettingsProvider

logger = logging.getLogger(__name__)

class MediaVersionManager:
    """
    Manager class to orchestrate the asynchronous creation of additional
    media item versions. Versions include:
      - Watermarked preview
      - Full watermarked version
      - Blurred thumbnail
      - Blurred preview

    If 'regenerate' is False, versions will only be created if they do not exist.
    If 'regenerate' is True, existing versions will be deleted and new ones will be created.
    """

    def __init__(self, media_item_id: int):
        self.media_item_id = media_item_id
        try:
            self.media_item = MediaItem.objects.get(id=media_item_id)
        except MediaItem.DoesNotExist:
            raise ValueError(f"MediaItem with ID {media_item_id} does not exist.")

        # Fetch configuration settings for this media item
        self.config = MediaSettingsProvider.get_all_settings()

    def _should_create(self, version_type: int, regenerate: bool) -> bool:
        """
        Check whether to create a new version.
        If 'regenerate' is True, delete any existing versions and return True.
        Otherwise, only return True if the version does not exist.
        """
        existing_versions = self.media_item.versions.filter(version_type=version_type)
        if regenerate:
            if existing_versions.exists():
                existing_versions.delete()
            return True
        else:
            return not existing_versions.exists()

    def process_versions(self, regenerate: bool = False):
        """
        Process and generate all additional versions for the given media item.
        Only create a version if it doesn't exist unless 'regenerate' is True.
        """
        # Watermarked preview version
        if self._should_create(MediaItemVersion.PREVIEW, regenerate):
            try:
                preview_file = watermark.create_watermarked_preview(
                    self.media_item,
                    quality=self.config["watermarked_preview_quality"],
                    preview_size=self.config["preview_size"]
                )
                media_version_creator.create_media_item_version(
                    media_item=self.media_item,
                    file_obj=preview_file,
                    version_type=MediaItemVersion.PREVIEW,
                    is_image=True
                )
            except Exception as e:
                logger.error("Error generating watermarked preview: %s", e)
        else:
            logger.info("Watermarked preview version already exists for MediaItem %s", self.media_item.id)

        # Full watermarked version (for paid users)
        if self._should_create(MediaItemVersion.WATERMARKED, regenerate):
            try:
                full_watermarked_file = watermark.create_full_watermarked_version(
                    self.media_item,
                    quality=self.config["full_watermarked_version_quality"]
                )
                media_version_creator.create_media_item_version(
                    media_item=self.media_item,
                    file_obj=full_watermarked_file,
                    version_type=MediaItemVersion.WATERMARKED,
                    is_image=True
                )
            except Exception as e:
                logger.error("Error generating full watermarked version: %s", e)
        else:
            logger.info("Full watermarked version already exists for MediaItem %s", self.media_item.id)

        # Blurred thumbnail version
        if self._should_create(MediaItemVersion.BLURRED_THUMBNAIL, regenerate):
            try:
                # Retrieve existing thumbnail version (assumed to exist)
                thumbnail_version = self.media_item.versions.get(version_type=MediaItemVersion.THUMBNAIL)
                blurred_thumbnail = watermark.create_blurred_thumbnail(
                    thumbnail_version.file,
                    quality=self.config["blurred_thumbnail_quality"],
                    thumbnail_size=self.config["thumbnail_size"]
                )
                media_version_creator.create_media_item_version(
                    media_item=self.media_item,
                    file_obj=blurred_thumbnail,
                    version_type=MediaItemVersion.BLURRED_THUMBNAIL,
                    is_image=True
                )
            except Exception as e:
                logger.error("Error generating blurred thumbnail: %s", e)
        else:
            logger.info("Blurred thumbnail version already exists for MediaItem %s", self.media_item.id)

        # Blurred preview version
        if self._should_create(MediaItemVersion.BLURRED_PREVIEW, regenerate):
            try:
                blurred_preview = watermark.create_blurred_preview(
                    self.media_item,
                    quality=self.config["blurred_preview_quality"],
                    preview_size=self.config["preview_size"]  # Using preview size setting
                )
                media_version_creator.create_media_item_version(
                    media_item=self.media_item,
                    file_obj=blurred_preview,
                    version_type=MediaItemVersion.BLURRED_PREVIEW,
                    is_image=True
                )
            except Exception as e:
                logger.error("Error generating blurred preview: %s", e)
        else:
            logger.info("Blurred preview version already exists for MediaItem %s", self.media_item.id)
