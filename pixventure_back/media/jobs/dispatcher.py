# media/tasks/dispatcher.py
from media.tasks import process_media_item_versions

class TaskDispatcher:
    @staticmethod
    def dispatch_media_item_versions(media_item_id: int, regenerate: bool = False, allowed_versions: list = None):
        """
        Dispatch the asynchronous task to process media item versions with additional parameters.
        """
        return process_media_item_versions.delay(media_item_id, regenerate, allowed_versions)
