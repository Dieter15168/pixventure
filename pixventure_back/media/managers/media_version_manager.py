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
    """

    def __init__(self, media_item_id: int):
        self.media_item_id = media_item_id
        try:
            self.media_item = MediaItem.objects.get(id=media_item_id)
        except MediaItem.DoesNotExist:
            raise ValueError(f"MediaItem with ID {media_item_id} does not exist.")

        # Fetch configuration settings for this media item
        self.config = MediaSettingsProvider.get_all_settings()

    def process_versions(self):
        """
        Process and generate all additional versions for the given media item,
        only if they don't already exist.
        """
        existing_types = {v.version_type for v in self.media_item.versions.all()}

        # Watermarked preview version
        if MediaItemVersion.PREVIEW not in existing_types:
            try:
                preview_file = watermark.create_watermarked_preview(
                    self.media_item, quality=self.config["watermarked_preview_quality"]
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
        if MediaItemVersion.WATERMARKED not in existing_types:
            try:
                full_watermarked_file = watermark.create_full_watermarked_version(
                    self.media_item, quality=self.config["full_watermarked_version_quality"]
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
        if MediaItemVersion.BLURRED_THUMBNAIL not in existing_types:
            try:
                # Retrieve existing thumbnail version (assumed to exist)
                thumbnail_version = self.media_item.versions.get(version_type=MediaItemVersion.THUMBNAIL)
                blurred_thumbnail = watermark.create_blurred_thumbnail(
                    thumbnail_version.file, quality=self.config["blurred_thumbnail_quality"]
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
        if MediaItemVersion.BLURRED_PREVIEW not in existing_types:
            try:
                blurred_preview = watermark.create_blurred_preview(
                    self.media_item, quality=self.config["blurred_preview_quality"]
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
