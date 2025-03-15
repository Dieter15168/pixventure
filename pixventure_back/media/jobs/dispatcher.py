# media/jobs/dispatcher.py
"""
Abstraction for dispatching asynchronous tasks.
This module encapsulates the call to Celery so that future changes to the task queue mechanism
will require minimal code changes elsewhere.
"""

from media.tasks import process_media_item_versions

class TaskDispatcher:
    @staticmethod 
    def dispatch_media_item_versions(media_item_id: int):
        """
        Dispatch the asynchronous task to process media item versions.
        
        :param media_item_id: ID of the MediaItem to process.
        :return: AsyncResult from the task queue system.
        """
        return process_media_item_versions.delay(media_item_id)
