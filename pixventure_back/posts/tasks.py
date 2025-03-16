# posts/tasks.py
from celery import shared_task
from posts.managers.post_publication_manager import PostPublicationManager

@shared_task(name="posts.tasks.publish_post")
def publish_post_task(post_id, force=False):
    """
    Celery task to publish a post.
    
    :param post_id: ID of the post to publish.
    :param force: If True, override some checks.
    """
    result = PostPublicationManager.publish_post(post_id, force=force)
    return result
