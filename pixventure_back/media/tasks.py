# media/tasks.py
"""
This module exists for Celery autodiscovery.
It defines a single generic task that delegates to the appropriate handler.
"""
from celery import shared_task
import logging
from media.managers.media_versions import media_version_handlers
from media.managers.hashing import media_hash_handlers
from media.managers.duplicates.duplicate_handlers import handle_duplicate_detection

logger = logging.getLogger(__name__)

# Mapping handler names to functions.
HANDLER_MAPPING = {
    "image_preview": media_version_handlers.handle_image_preview,
    "image_full_watermarked": media_version_handlers.handle_image_full_watermarked,
    "image_blurred_thumbnail": media_version_handlers.handle_image_blurred_thumbnail,
    "image_blurred_preview": media_version_handlers.handle_image_blurred_preview,
    "video_watermarked": media_version_handlers.handle_video_watermarked,
    "video_preview": media_version_handlers.handle_video_preview,
    "video_thumbnail": media_version_handlers.handle_video_thumbnail,
    "fuzzy_hash": media_hash_handlers.handle_fuzzy_hash,
    "duplicate_detection": handle_duplicate_detection,
}

@shared_task(name="media.tasks.run_version_task")
def run_version_task(task_name, media_item_id, config, regenerate=False):
    """
    Generic task that looks up the appropriate handler based on task_name.
    """
    try:
        handler = HANDLER_MAPPING.get(task_name)
        if not handler:
            raise ValueError(f"Handler for task '{task_name}' not found.")
        result = handler(media_item_id, config, regenerate)
        return result
    except Exception as e:
        logger.error("Error in task %s for MediaItem %s: %s", task_name, media_item_id, e)
        raise e

@shared_task(name="media.tasks.run_duplicate_detection")
def run_duplicate_detection(input_data, config=None, regenerate=False):
    """
    Task for performing duplicate detection.
    
    It expects `input_data` to be the context dictionary from the fuzzy hash task,
    containing keys like 'media_item_version_id', 'hash_value', and 'hash_type'.
    """
    if config is None:
        config = {}
    try:
        result = handle_duplicate_detection(input_data, config, regenerate)
        return result
    except Exception as e:
        logger.error("Error in duplicate detection: %s", e)
        raise e