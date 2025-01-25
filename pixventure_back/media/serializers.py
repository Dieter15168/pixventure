from rest_framework import serializers
from .models import MediaItem
from social.utils import user_has_liked
from media.utils import get_media_file_for_display

class MediaItemSerializer(serializers.ModelSerializer):
    """
    Returns core information about a MediaItem:
    - item id
    - item type (Photo/Video)
    - likes_counter
    - whether current user has liked it
    - a "thumbnail" or "preview" URL
    """
    id = serializers.IntegerField(read_only=True, source='pk')
    has_liked = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = MediaItem
        fields = [
            'id',
            'item_type',
            'likes_counter',
            'has_liked',
            'thumbnail_url',
        ]

    def get_has_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return user_has_liked(request.user, media_item=obj)
        return False

    def get_thumbnail_url(self, obj):
        request = self.context.get('request')
        user = request.user if request else None
        # Retrieve the post from context (defaulting to None if not present)
        post = self.context.get('post', None)

        # If we don't have a "post" context, pass None or self.context.get('post')
        return get_media_file_for_display(
            media_item=obj,
            user=user,
            post=post,
            thumbnail=True
        )