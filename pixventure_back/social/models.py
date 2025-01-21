from django.db import models
from django.contrib.auth import get_user_model
from posts.models import Post
from media.models import MediaItem

User = get_user_model()

class Like(models.Model):
    """
    Represents a 'like' action by a user on either a Post or a MediaItem.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, null=True, blank=True, on_delete=models.CASCADE)
    media_item = models.ForeignKey(MediaItem, null=True, blank=True, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Like by {self.user} on {self.post or self.media_item}"
