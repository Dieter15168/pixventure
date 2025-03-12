# media/serializers.py

from rest_framework import serializers
from .models import MediaItem, MediaItemVersion
from social.utils import user_has_liked
from media.utils.media_file import get_media_file_for_display


class TileInfoMixin(serializers.Serializer):
    tile_size = serializers.SerializerMethodField()

    def get_tile_size(self, obj):
        dims = self.get_featured_image_dimensions(obj)
        if not dims:
            return "small"  # default if no dimensions
        width, height = dims
        try:
            ratio = width / height
        except ZeroDivisionError:
            return "small"
        if ratio <= 0.8:
            return "large"
        elif ratio <= 1.2:
            return "medium"
        else:
            return "small"

    def get_featured_image_dimensions(self, obj):
        """
        This method must be implemented by the subclass.
        It should return a tuple: (width, height)
        or None if dimensions cannot be determined.
        """
        raise NotImplementedError("Subclasses must implement get_featured_image_dimensions")


class MediaItemSerializer(TileInfoMixin, serializers.ModelSerializer):
    """
    Returns core information about a MediaItem:
    - id
    - media_type (as a verbose string: "photo" or "video")
    - likes_counter
    - whether current user has liked it
    - a thumbnail/preview URL
    """
    id = serializers.IntegerField(read_only=True, source='pk')
    media_type = serializers.SerializerMethodField()
    has_liked = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = MediaItem
        fields = [
            'id',
            'media_type',
            'likes_counter',
            'has_liked',
            'thumbnail_url',
            'tile_size',
        ]

    def get_media_type(self, obj):
        # Convert numeric value to verbose string.
        if obj.media_type == MediaItem.PHOTO:
            return "photo"
        elif obj.media_type == MediaItem.VIDEO:
            return "video"
        return "unknown"

    def get_has_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return user_has_liked(request.user, media_item=obj)
        return False

    def get_thumbnail_url(self, obj):
        request = self.context.get('request')
        user = request.user if request else None
        post = self.context.get('post', None)
        return get_media_file_for_display(
            media_item=obj,
            user=user,
            post=post,
            thumbnail=True
        )
        
    # TileInfoMixin's required method:
    def get_featured_image_dimensions(self, obj):
        thumbnail = obj.versions.filter(version_type=MediaItemVersion.THUMBNAIL).first()
        if thumbnail and thumbnail.width and thumbnail.height:
            return (thumbnail.width, thumbnail.height)
        return None
    

class UnpublishedMediaItemSerializer(serializers.ModelSerializer):
    """
    Minimal info for user-owned media items that haven't been published, etc.:
      - id
      - a verbose "media_type" ("photo"/"video")
      - a verbose "status"
      - the .file.url from the THUMBNAIL version
      - width, height, file_size from the ORIGINAL version
    """
    media_type = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    width = serializers.SerializerMethodField()
    height = serializers.SerializerMethodField()
    file_size = serializers.SerializerMethodField()

    class Meta:
        model = MediaItem
        fields = [
            "id",
            "media_type",
            "status",
            "thumbnail_url",
            "width",
            "height",
            "file_size",
        ]

    def get_media_type(self, obj):
        if obj.media_type == MediaItem.PHOTO:
            return "photo"
        elif obj.media_type == MediaItem.VIDEO:
            return "video"
        return "unknown"

    def get_status(self, obj):
        return obj.get_status_display()

    def get_thumbnail_url(self, obj):
        thumb_version = obj.versions.filter(version_type=MediaItemVersion.THUMBNAIL).first()
        if thumb_version and thumb_version.file:
            return thumb_version.file.url
        return ""

    def get_width(self, obj):
        orig_version = obj.versions.filter(version_type=MediaItemVersion.ORIGINAL).first()
        return orig_version.width if orig_version else None

    def get_height(self, obj):
        orig_version = obj.versions.filter(version_type=MediaItemVersion.ORIGINAL).first()
        return orig_version.height if orig_version else None

    def get_file_size(self, obj):
        orig_version = obj.versions.filter(version_type=MediaItemVersion.ORIGINAL).first()
        return orig_version.file_size if orig_version else None