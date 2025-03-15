# media/tasks/dispatcher.py
from media.tasks import process_media_item_versions, compute_fuzzy_hash_task

class TaskDispatcher:
    @staticmethod
    def dispatch_media_item_versions(media_item_id: int, regenerate: bool = False, allowed_versions: list = None):
        """
        Dispatch the asynchronous task to process media item versions.
        """
        return process_media_item_versions.delay(media_item_id, regenerate, allowed_versions)
    
    @staticmethod
    def dispatch_fuzzy_hash(media_item_version_id: int, hash_type="phash"):
        """
        Dispatch the asynchronous task to compute the fuzzy hash.
        """
        return compute_fuzzy_hash_task.delay(media_item_version_id, hash_type)
