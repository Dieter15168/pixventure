# social/models.py
from django.db import models
from django.contrib.auth import get_user_model
from posts.models import Post
from media.models import MediaItem
from albums.models import Album

User = get_user_model()

class Like(models.Model):
    """
    Represents a 'like' action by a user (liking_user) on a target,
    which can be a Post, MediaItem, Album, or another User (liked_user).
    """
    liking_user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, null=True, blank=True, on_delete=models.CASCADE)
    media_item = models.ForeignKey(MediaItem, null=True, blank=True, on_delete=models.CASCADE)
    album = models.ForeignKey(Album, null=True, blank=True, on_delete=models.CASCADE)
    liked_user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name="likes_received")

    is_active = models.BooleanField(default=True)  # Is this like active or canceled?
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        target = self.post or self.media_item or self.album or self.liked_user
        return f"Like by {self.liking_user} on {target} (active={self.is_active})"
