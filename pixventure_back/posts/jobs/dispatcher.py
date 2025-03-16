# posts/tasks/dispatcher.py
from posts.tasks import publish_post_task

class PostTaskDispatcher:
    @staticmethod
    def dispatch_publish_post(post_id, force=False):
        """
        Dispatch a task to publish a post.
        """
        return publish_post_task.delay(post_id, force)
