# albums/serializers.py

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Album, AlbumElement
from media.models import MediaItem
from posts.models import Post

# Import your existing Post and MediaItem serializers from their respective apps
from posts.serializers import PostSerializer
from media.serializers import MediaItemSerializer

User = get_user_model()


class AlbumListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing albums in /api/albums/.
    Includes minimal or summary fields:
      - id, name, slug
      - likes_counter
      - owner_username (if show_creator_to_others is True)
    """
    owner_username = serializers.SerializerMethodField()

    class Meta:
        model = Album
        fields = [
            'id',
            'name',
            'slug',
            'likes_counter',
            'owner_username',
        ]

    def get_owner_username(self, obj):
        if obj.show_creator_to_others and obj.owner:
            return obj.owner.username
        return None


class AlbumDetailSerializer(serializers.ModelSerializer):
    """
    Shows detailed info about the album, including:
      - id, name, slug, status
      - likes_counter
      - counts for posts, images, and videos in the album
      - owner_username
    """
    owner_username = serializers.SerializerMethodField()
    posts_count = serializers.SerializerMethodField()
    images_count = serializers.SerializerMethodField()
    videos_count = serializers.SerializerMethodField()

    class Meta:
        model = Album
        fields = [
            'id',
            'name',
            'slug',
            'status',
            'likes_counter',
            'posts_count',
            'images_count',
            'videos_count',
            'owner_username',
            'show_creator_to_others',
            'created',
            'updated',
        ]

    def get_owner_username(self, obj):
        if obj.show_creator_to_others and obj.owner:
            return obj.owner.username
        return None

    def get_posts_count(self, obj):
        return obj.album_elements.filter(element_type=AlbumElement.POST_TYPE).count()

    def get_images_count(self, obj):
        return obj.album_elements.filter(
            element_type=AlbumElement.MEDIA_TYPE,
            element_media__item_type=MediaItem.PHOTO
        ).count()

    def get_videos_count(self, obj):
        return obj.album_elements.filter(
            element_type=AlbumElement.MEDIA_TYPE,
            element_media__item_type=MediaItem.VIDEO
        ).count()


class AlbumElementSerializer(serializers.ModelSerializer):
    """
    An album element referencing either a Post or a MediaItem.
    Reuses PostSerializer / MediaItemSerializer for data, 
    preventing redundant logic.
    """
    post_data = serializers.SerializerMethodField()
    media_data = serializers.SerializerMethodField()

    class Meta:
        model = AlbumElement
        fields = [
            'id',
            'element_type',
            'position',
            'created',
            'updated',
            'post_data',   # Reuse PostSerializer
            'media_data',  # Reuse MediaItemSerializer
        ]

    def get_post_data(self, obj):
        """
        If element references a Post, use PostSerializer.
        """
        if obj.element_type == AlbumElement.POST_TYPE and obj.element_post:
            # Pass the request in context so that PostSerializer can handle 
            # paywall / blur logic if needed
            return PostSerializer(
                obj.element_post,
                context=self.context
            ).data
        return None

    def get_media_data(self, obj):
        """
        If element references a MediaItem, use MediaItemSerializer.
        """
        if obj.element_type == AlbumElement.MEDIA_TYPE and obj.element_media:
            return MediaItemSerializer(
                obj.element_media,
                context=self.context
            ).data
        return None
