from rest_framework import serializers
from posts.models import Post
from media.models import MediaItem
from social.models import Like

class PostSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True, source='pk')
    images_count = serializers.SerializerMethodField()
    videos_count = serializers.SerializerMethodField()
    has_liked = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id',
            'name',
            'likes_counter',
            'images_count',
            'videos_count',
            'has_liked',
            'thumbnail_url',
        ]

    def get_images_count(self, obj):
        # Query PostMedia for this post, counting items that are PHOTOS
        return obj.post_media_links.filter(media_item__item_type=MediaItem.PHOTO).count()

    def get_videos_count(self, obj):
        # Query PostMedia for this post, counting items that are VIDEOS
        return obj.post_media_links.filter(media_item__item_type=MediaItem.VIDEO).count()

    def get_has_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Like.objects.filter(post=obj, user=request.user).exists()
        return False

    def get_thumbnail_url(self, obj):
        featured = obj.featured_item
        if featured:
            if featured.item_type == MediaItem.PHOTO and featured.thumbnail_file:
                return featured.thumbnail_file.url
            if featured.item_type == MediaItem.VIDEO and featured.preview_file:
                return featured.preview_file.url
        return None


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
            return Like.objects.filter(media_item=obj, user=request.user).exists()
        return False

    def get_thumbnail_url(self, obj):
        # For photos, you might show `thumbnail_file`; for videos, `preview_file`.
        if obj.item_type == MediaItem.PHOTO and obj.thumbnail_file:
            return obj.thumbnail_file.url
        elif obj.item_type == MediaItem.VIDEO and obj.preview_file:
            return obj.preview_file.url
        return None


class MediaItemInPostSerializer(serializers.Serializer):
    """
    Serializer for a single item in a post, including:
    - item_id
    - id of previous item
    - id of next item
    - item_url (could be original_file or whatever is needed)
    """
    item_id = serializers.IntegerField()
    previous_item_id = serializers.IntegerField(allow_null=True)
    next_item_id = serializers.IntegerField(allow_null=True)
    item_url = serializers.CharField()
