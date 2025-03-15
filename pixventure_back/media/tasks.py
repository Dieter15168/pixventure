# media/tasks.py
from celery import shared_task
from media.managers.media_version_manager import MediaVersionManager

@shared_task  # Removed the explicit name
def process_media_item_versions(media_item_id: int, regenerate: bool = False, allowed_versions: list = None):
    """
    Asynchronously processes and generates additional versions
    for the media item with the given ID.
    Only the versions specified in 'allowed_versions' will be processed.
    """
    manager = MediaVersionManager(media_item_id)
    manager.process_versions(regenerate=regenerate, allowed_versions=allowed_versions)
