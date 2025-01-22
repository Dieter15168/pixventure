from rest_framework import serializers
from posts.models import Post
from posts.models import PostMedia
from media.models import MediaItem
from social.utils import user_has_liked
from media.utils import get_media_file_for_display

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
            return user_has_liked(request.user, post=obj)
        return False

    def get_thumbnail_url(self, obj):
        """
        Return the appropriate thumbnail for the featured media item, 
        respecting paywall and blur logic.
        """
        request = self.context.get('request')
        user = request.user if request else None
        featured = obj.featured_item

        # If there's no featured item, return None
        if not featured:
            return None

        return get_media_file_for_display(
            media_item=featured,  # We pass the MediaItem itself
            user=user,
            post=obj,  # in case the post is blurred
            thumbnail=True  # we want the 'thumbnail' variant
        )


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


class PostMediaItemDetailSerializer(serializers.ModelSerializer):
    """
    Serializes a single PostMedia object, returning:
    - item_id: The ID of the MediaItem
    - likes_counter: Number of likes on that MediaItem
    - has_liked: Whether the current user has liked this MediaItem
    - previous_item_id: ID of the previous MediaItem in the same Post
    - next_item_id: ID of the next MediaItem in the same Post
    - item_url: The URL for the MediaItem file (e.g., original_file.url)
    """

    item_id = serializers.SerializerMethodField()
    likes_counter = serializers.SerializerMethodField()
    has_liked = serializers.SerializerMethodField()
    previous_item_id = serializers.SerializerMethodField()
    next_item_id = serializers.SerializerMethodField()
    item_url = serializers.SerializerMethodField()

    class Meta:
        model = PostMedia
        fields = [
            'item_id',
            'likes_counter',
            'has_liked',
            'previous_item_id',
            'next_item_id',
            'item_url',
        ]

    def get_item_id(self, obj):
        """Return the primary key of the related MediaItem."""
        return obj.media_item.id

    def get_likes_counter(self, obj):
        """How many likes does this MediaItem have?"""
        return obj.media_item.likes_counter

    def get_has_liked(self, obj):
        """
        Checks if the current user has liked this specific MediaItem,
        using our DRY utility function.
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return user_has_liked(request.user, media_item=obj.media_item)
        return False

    def get_previous_item_id(self, obj):
        """
        Retrieves the ID of the previous MediaItem in the same Post, 
        based on the position field in PostMedia.
        """
        current_position = obj.position
        prev_pm = (
            PostMedia.objects
            .filter(post=obj.post, position__lt=current_position)
            .order_by('-position')
            .first()
        )
        return prev_pm.media_item_id if prev_pm else None

    def get_next_item_id(self, obj):
        """
        Retrieves the ID of the next MediaItem in the same Post,
        based on the position field in PostMedia.
        """
        current_position = obj.position
        next_pm = (
            PostMedia.objects
            .filter(post=obj.post, position__gt=current_position)
            .order_by('position')
            .first()
        )
        return next_pm.media_item_id if next_pm else None

    def get_item_url(self, obj):
        """Return an appropriate URL for the file."""
        request = self.context.get('request')
        user = request.user if request else None
        media_item = obj.media_item

        if not media_item:
            return ""

        # We assume in "PostMedia" we can do obj.post to see if post is blurred
        return get_media_file_for_display(
            media_item=media_item,
            user=user,
            post=obj.post,
            thumbnail=False  # we want the "full" version
        )
