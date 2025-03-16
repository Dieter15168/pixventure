# media/managers/media_version_scheduler.py
import logging
from media.models import MediaItem, MediaItemVersion
from media.jobs import dispatcher

logger = logging.getLogger(__name__)

def schedule_versions(media_item, config, allowed_versions, regenerate=False):
    """
    Schedules version creation for a media item.
    For images, tasks are dispatched concurrently.
    For videos, tasks are dispatched as a chain.
    """
    from media.models import MediaItem
    if media_item.media_type == MediaItem.VIDEO:
        _schedule_video_versions(media_item, config, allowed_versions, regenerate)
    elif media_item.media_type == MediaItem.PHOTO:
        _schedule_image_versions(media_item, config, allowed_versions, regenerate)
    else:
        logger.info("Unsupported media type for MediaItem %s", media_item.id)

def _schedule_image_versions(media_item, config, allowed_versions, regenerate):
    task_list = []
    for version in allowed_versions:
        task_name = _get_image_task_name(version)
        if task_name:
            task_list.append({
                'task_name': task_name,
                'media_item_id': media_item.id,
                'config': config,
                'regenerate': regenerate
            })
    if task_list:
        dispatcher.dispatch_concurrent(task_list)
        logger.info("Dispatched concurrent image tasks for MediaItem %s", media_item.id)
    else:
        logger.info("No image tasks to dispatch for MediaItem %s", media_item.id)

def _schedule_video_versions(media_item, config, allowed_versions, regenerate):
    task_list = []
    # Define the chain order for video tasks: watermarked -> preview -> thumbnail.
    if MediaItemVersion.WATERMARKED in allowed_versions:
        task_list.append({
            'task_name': "video_watermarked",
            'media_item_id': media_item.id,
            'config': config,
            'regenerate': regenerate
        })
    if MediaItemVersion.PREVIEW in allowed_versions:
        task_list.append({
            'task_name': "video_preview",
            'media_item_id': media_item.id,
            'config': config,
            'regenerate': regenerate
        })
    if MediaItemVersion.THUMBNAIL in allowed_versions:
        task_list.append({
            'task_name': "video_thumbnail",
            'media_item_id': media_item.id,
            'config': config,
            'regenerate': regenerate
        })
    if task_list:
        dispatcher.dispatch_chain(task_list)
        logger.info("Dispatched video task chain for MediaItem %s", media_item.id)
    else:
        logger.info("No video tasks to dispatch for MediaItem %s", media_item.id)

def _get_image_task_name(version_type):
    mapping = {
        MediaItemVersion.PREVIEW: "image_preview",
        MediaItemVersion.WATERMARKED: "image_full_watermarked",
        MediaItemVersion.BLURRED_THUMBNAIL: "image_blurred_thumbnail",
        MediaItemVersion.BLURRED_PREVIEW: "image_blurred_preview",
    }
    return mapping.get(version_type)
