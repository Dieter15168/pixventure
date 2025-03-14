# albums/serializers.py

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Album, AlbumElement
from main.utils import generate_unique_slug
from media.models import MediaItem, MediaItemVersion
from social.utils import user_has_liked
from media.utils.media_file import get_media_file_for_display
from posts.serializers import PostSerializer
from media.serializers import MediaItemSerializer, TileInfoMixin

User = get_user_model()


class AlbumCreateSerializer(serializers.ModelSerializer):
    """
    Creates a new album. The user only supplies the album name,
    a boolean is_public flag, and show_creator_to_others.
    The slug is auto-generated and status is set based on is_public.
    """
    is_public = serializers.BooleanField(write_only=True)
    
    class Meta:
        model = Album
        # Only allow input for name, is_public, and show_creator_to_others.
        fields = [
            'name',
            'is_public',
            'show_creator_to_others',
        ]

    def create(self, validated_data):
        is_public = validated_data.pop('is_public', False)
        name = validated_data.get('name')
        validated_data['slug'] = generate_unique_slug(Album, name, max_length=255)
        # Set status based on is_public:
        if is_public:
            validated_data['status'] = Album.PENDING_MODERATION
        else:
            validated_data['status'] = Album.PRIVATE
        return super().create(validated_data)


class AlbumListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing albums in /api/albums/.
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


class AlbumDetailSerializer(TileInfoMixin, serializers.ModelSerializer):
    owner_username = serializers.SerializerMethodField()
    posts_count = serializers.SerializerMethodField()
    images_count = serializers.SerializerMethodField()
    videos_count = serializers.SerializerMethodField()
    has_liked = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()

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
            'has_liked',
            'thumbnail_url',
            'owner_username',
            'show_creator_to_others',
            'created',
            'updated',
            'tile_size',
            'can_edit',
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
            element_media__media_type=MediaItem.PHOTO
        ).count()

    def get_videos_count(self, obj):
        return obj.album_elements.filter(
            element_type=AlbumElement.MEDIA_TYPE,
            element_media__media_type=MediaItem.VIDEO
        ).count()

    def get_has_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return user_has_liked(request.user, album=obj)
        return False

    def get_thumbnail_url(self, obj):
        """
        Return the appropriate thumbnail for the featured media item.
        """
        request = self.context.get('request')
        user = request.user if request else None
        featured = obj.featured_item
        if not featured:
            return None
        return get_media_file_for_display(
            media_item=featured,
            user=user,
            thumbnail=True
        )
        
    # TileInfoMixin's required method:
    def get_featured_image_dimensions(self, obj):
        if not obj.featured_item:
            return None
        thumbnail = obj.featured_item.versions.filter(version_type=MediaItemVersion.THUMBNAIL).first()
        if thumbnail and thumbnail.width and thumbnail.height:
            return (thumbnail.width, thumbnail.height)
        return None

    def get_can_edit(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return (obj.owner == request.user) or request.user.is_staff
        return False



class AlbumElementSerializer(serializers.ModelSerializer):
    """
    An album element referencing either a Post or a MediaItem,
    reusing PostSerializer / MediaItemSerializer for data.
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
            'post_data',
            'media_data',
        ]

    def get_post_data(self, obj):
        """
        If element references a Post, use PostSerializer.
        """
        if obj.element_type == AlbumElement.POST_TYPE and obj.element_post:
            return PostSerializer(obj.element_post, context=self.context).data
        return None

    def get_media_data(self, obj):
        """
        If element references a MediaItem, use MediaItemSerializer.
        """
        if obj.element_type == AlbumElement.MEDIA_TYPE and obj.element_media:
            return MediaItemSerializer(obj.element_media, context=self.context).data
        return None


class AlbumElementCreateSerializer(serializers.ModelSerializer):
    # Accept element_type as a string and element_id as the identifier
    element_type = serializers.CharField()
    element_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = AlbumElement
        fields = ['element_type', 'element_id']

    def validate_element_type(self, value):
        value = value.lower()
        if value not in ['post', 'media']:
            raise serializers.ValidationError("element_type must be 'post' or 'media'.")
        return value

    def create(self, validated_data):
        album = self.context.get('album')  # Provided by the view
        element_type_str = validated_data.pop('element_type').lower()
        element_id = validated_data.pop('element_id')
        if element_type_str == 'post':
            validated_data['element_type'] = AlbumElement.POST_TYPE
            validated_data['element_post_id'] = element_id
        elif element_type_str == 'media':
            validated_data['element_type'] = AlbumElement.MEDIA_TYPE
            validated_data['element_media_id'] = element_id
        validated_data['album'] = album
        return AlbumElement.objects.create(**validated_data)