from celery import shared_task
import logging
from posts.managers.post_publication.post_publication_handlers import handle_post_publication

logger = logging.getLogger(__name__)

# Mapping handler names to functions.
HANDLER_MAPPING = {
    "post_publication": handle_post_publication,
}

@shared_task(name="posts.tasks.run_post_task")
def run_post_task(task_name, post_id, config, regenerate=False):
    """
    Generic task that looks up the appropriate handler based on task_name and invokes it.
    """
    try:
        handler = HANDLER_MAPPING.get(task_name)
        if not handler:
            raise ValueError(f"Handler for task '{task_name}' not found.")
        result = handler(post_id, config, regenerate)
        return result
    except Exception as e:
        logger.error("Error in task %s for Post %s: %s", task_name, post_id, e)
        raise e
