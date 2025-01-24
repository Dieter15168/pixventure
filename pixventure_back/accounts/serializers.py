# serializers.py
from rest_framework import serializers
from .models import UserProfile
from django.contrib.auth import get_user_model

User = get_user_model()

class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for the UserProfile model.
    Currently returns the user's username.
    """
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = UserProfile
        fields = ['username']
