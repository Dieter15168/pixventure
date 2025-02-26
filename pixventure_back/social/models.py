from django.db import models
from django.contrib.auth import get_user_model
from posts.models import Post
from media.models import MediaItem
from albums.models import Album
from accounts.models import UserProfile

User = get_user_model()

class Like(models.Model):
    """
    Represents a 'like' action by a user on either a Post or a MediaItem.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, null=True, blank=True, on_delete=models.CASCADE)
    media_item = models.ForeignKey(MediaItem, null=True, blank=True, on_delete=models.CASCADE)
    album = models.ForeignKey(Album, null=True, blank=True, on_delete=models.CASCADE)
    user_profile = models.ForeignKey(UserProfile, null=True, blank=True, on_delete=models.CASCADE)
    
    is_active = models.BooleanField(default=True)  # Is this like still active or canceled
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        target = self.post or self.media_item or self.album or self.user_profile
        return f"Like by {self.user} on {target} (active={self.is_active})"
