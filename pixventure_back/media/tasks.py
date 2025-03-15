# media/tasks.py
from celery import shared_task
from media.managers.media_version_manager import MediaVersionManager

@shared_task
def process_media_item_versions(media_item_id: int):
    """
    Asynchronously processes and generates additional versions
    for the media item with the given ID.
    
    :param media_item_id: ID of the MediaItem to process.
    """
    manager = MediaVersionManager(media_item_id)
    manager.process_versions()
