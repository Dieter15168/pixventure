# posts/managers/post_publication/post_publication_manager.py
import logging
from posts.jobs.dispatcher import dispatch_post_publication

logger = logging.getLogger(__name__)

class PostPublicationManager:
    """
    Central manager to publish a post.
    
    Other components can call PostPublicationManager.publish_post(post_id, force)
    to schedule publication. This manager pushes the task to the dispatcher.
    """
    @staticmethod
    def publish_post(post_id, force=False):
        config = {"force": force}
        # Dispatch the publication task.
        result = dispatch_post_publication(post_id, config, regenerate=False)
        logger.info(f"Dispatched publication task for Post {post_id} with force={force}.")
        return result
