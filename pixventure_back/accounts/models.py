from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class UserProfile(models.Model):
    """
    Extends the built-in User model with additional profile data.
    For membership logic, we rely on a separate UserMembership model.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    # Add other user-specific fields here if needed:
    # e.g. avatar, bio, location, etc.

    def __str__(self):
        return f"Profile of {self.user.username}"
