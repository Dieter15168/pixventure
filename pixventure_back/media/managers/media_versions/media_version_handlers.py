# media/managers/media_version_handlers.py
import logging
from media.models import MediaItem, MediaItemVersion
from media.services import media_version_creator, watermark, video_processor

logger = logging.getLogger(__name__)

# ---------------------------
# Image Handlers
# ---------------------------
def handle_image_preview(media_item_id, config, regenerate=False):
    try:
        media_item = MediaItem.objects.get(id=media_item_id)
        preview_file = watermark.create_watermarked_preview(
            media_item,
            quality=config["watermarked_preview_quality"],
            preview_size=config["preview_size"]
        )
        media_version_creator.create_media_item_version(
            media_item=media_item,
            file_obj=preview_file,
            version_type=MediaItemVersion.PREVIEW,
            is_image=True
        )
        logger.info("Image preview created for MediaItem %s", media_item.id)
        return True
    except Exception as e:
        logger.error("Error in image preview handler: %s", e)
        return False

def handle_image_full_watermarked(media_item_id, config, regenerate=False):
    try:
        media_item = MediaItem.objects.get(id=media_item_id)
        full_file = watermark.create_full_watermarked_version(
            media_item,
            quality=config["full_watermarked_version_quality"],
            watermark_transparency=config["full_watermark_transparency"]
        )
        media_version_creator.create_media_item_version(
            media_item=media_item,
            file_obj=full_file,
            version_type=MediaItemVersion.WATERMARKED,
            is_image=True
        )
        logger.info("Full watermarked image created for MediaItem %s", media_item.id)
        return True
    except Exception as e:
        logger.error("Error in full watermarked image handler: %s", e)
        return False

def handle_image_blurred_thumbnail(media_item_id, config, regenerate=False):
    try:
        media_item = MediaItem.objects.get(id=media_item_id)
        # Assumes that a THUMBNAIL version already exists.
        thumbnail_version = media_item.versions.get(version_type=MediaItemVersion.THUMBNAIL)
        blurred_file = watermark.create_blurred_thumbnail(
            thumbnail_version.file,
            quality=config["blurred_thumbnail_quality"],
            thumbnail_size=config["thumbnail_size"],
            blur_radius=config["thumbnail_blur_radius"]
        )
        media_version_creator.create_media_item_version(
            media_item=media_item,
            file_obj=blurred_file,
            version_type=MediaItemVersion.BLURRED_THUMBNAIL,
            is_image=True
        )
        logger.info("Blurred thumbnail created for MediaItem %s", media_item.id)
        return True
    except Exception as e:
        logger.error("Error in blurred thumbnail handler: %s", e)
        return False

def handle_image_blurred_preview(media_item_id, config, regenerate=False):
    try:
        media_item = MediaItem.objects.get(id=media_item_id)
        blurred_file = watermark.create_blurred_preview(
            media_item,
            quality=config["blurred_preview_quality"],
            preview_size=config["preview_size"],
            blur_radius=config["preview_blur_radius"]
        )
        media_version_creator.create_media_item_version(
            media_item=media_item,
            file_obj=blurred_file,
            version_type=MediaItemVersion.BLURRED_PREVIEW,
            is_image=True
        )
        logger.info("Blurred preview created for MediaItem %s", media_item.id)
        return True
    except Exception as e:
        logger.error("Error in blurred preview handler: %s", e)
        return False

# ---------------------------
# Video Handlers
# ---------------------------
def handle_video_watermarked(media_item_id, config, regenerate=False):
    try:
        media_item = MediaItem.objects.get(id=media_item_id)
        watermarked_file, duration = video_processor.create_watermarked_video(
            media_item,
            quality=config["full_watermarked_version_quality"],
            max_video_bitrate=config["max_video_bitrate"]
        )
        # Update original version with duration.
        original_version = media_item.versions.get(version_type=MediaItemVersion.ORIGINAL)
        original_version.video_duration = duration
        original_version.save()
        
        media_version_creator.create_media_item_version(
            media_item=media_item,
            file_obj=watermarked_file,
            version_type=MediaItemVersion.WATERMARKED,
            is_image=False
        )
        logger.info("Watermarked video created for MediaItem %s", media_item.id)
        return True
    except Exception as e:
        logger.error("Error in video watermarked handler: %s", e)
        return False

def handle_video_preview(media_item_id, config, regenerate=False):
    try:
        media_item = MediaItem.objects.get(id=media_item_id)
        preview_file = video_processor.create_video_preview(
            media_item,
            quality=config["preview_video_quality"],
            preview_duration=config["preview_video_duration"]
        )
        media_version_creator.create_media_item_version(
            media_item=media_item,
            file_obj=preview_file,
            version_type=MediaItemVersion.PREVIEW,
            is_image=False
        )
        logger.info("Video preview created for MediaItem %s", media_item.id)
        return True
    except Exception as e:
        logger.error("Error in video preview handler: %s", e)
        return False

def handle_video_thumbnail(media_item_id, config, regenerate=False):
    try:
        media_item = MediaItem.objects.get(id=media_item_id)
        thumbnail_file = video_processor.create_video_thumbnail(media_item)
        media_version_creator.create_media_item_version(
            media_item=media_item,
            file_obj=thumbnail_file,
            version_type=MediaItemVersion.THUMBNAIL,
            is_image=False
        )
        logger.info("Video thumbnail created for MediaItem %s", media_item.id)
        return True
    except Exception as e:
        logger.error("Error in video thumbnail handler: %s", e)
        return False
