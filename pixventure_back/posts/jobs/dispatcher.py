from posts.tasks import run_post_task
import logging

logger = logging.getLogger(__name__)

def dispatch_post_publication(post_id, config, regenerate=False):
    """
    Return an immutable task signature for post publication.
    """
    return run_post_task.si("post_publication", post_id, config, regenerate).apply_async(ignore_result=True)
