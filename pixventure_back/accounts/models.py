from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class UserProfile(models.Model):
    """
    Extends the built-in User model with additional profile data.
    For membership logic, we rely on a separate UserMembership model.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    likes_counter = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile of {self.user.username}"
