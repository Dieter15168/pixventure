from rest_framework import serializers
from posts.models import Post
from posts.models import PostMedia
from media.models import MediaItem, MediaItemVersion
from social.utils import user_has_liked
from media.utils.media_file import get_media_file_for_display
from media.serializers import TileInfoMixin

class PostSerializer(TileInfoMixin, serializers.ModelSerializer):
    """
    Returns core information about a Post, including:
    - post id
    - name
    - likes_counter
    - number of images
    - number of videos
    - whether current user has liked this post
    - post thumbnail URL
    - owner's username
    """
    id = serializers.IntegerField(read_only=True, source='pk')
    images_count = serializers.SerializerMethodField()
    videos_count = serializers.SerializerMethodField()
    has_liked = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    owner_username = serializers.CharField(source='owner.username', read_only=True)


    class Meta:
        model = Post
        fields = [
            'id',
            'name',
            'slug',
            'likes_counter',
            'images_count',
            'videos_count',
            'has_liked',
            'thumbnail_url',
            'owner_username',
            'tile_size',
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
        
    # TileInfoMixin's required method:
    def get_featured_image_dimensions(self, obj):
        # We assume that the Post has a featured_item field (a MediaItem)
        if not obj.featured_item:
            return None
        thumbnail = obj.featured_item.versions.filter(version_type=MediaItemVersion.THUMBNAIL).first()
        if thumbnail and thumbnail.width and thumbnail.height:
            return (thumbnail.width, thumbnail.height)
        return None


class PostMediaItemDetailSerializer(serializers.ModelSerializer):
    """
    Serializes a single PostMedia object for the item viewer, returning:
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


class PostCreateSerializer(serializers.ModelSerializer):
    """
    For creating a new post. 
    The user can provide name, slug, etc.
    The `owner` will be set automatically from request.user.
    """
    class Meta:
        model = Post
        fields = [
            'name',
            'slug',
            'text',
            'status',
            'main_category',
            'tags',
            'featured_item',
            'is_featured_post',
            'is_blurred',
        ]
        extra_kwargs = {
            'slug': {'required': True},
        }
        

class PostMetaSerializer(serializers.ModelSerializer):
    owner_username = serializers.SerializerMethodField()
    categories = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'name', 'slug', 'owner_username', 'categories', 'tags', 'can_edit']

    def get_owner_username(self, obj):
        return obj.owner.username if obj.owner else None

    def get_categories(self, obj):
        from taxonomy.serializers import TermSerializer
        queryset = obj.categories.all()
        return TermSerializer(queryset, many=True).data

    def get_tags(self, obj):
        from taxonomy.serializers import TermSerializer
        queryset = obj.tags.all()
        return TermSerializer(queryset, many=True).data

    def get_can_edit(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            # Example logic: user can edit if they own the post or have the change permission.
            return obj.owner == request.user or request.user.has_perm('posts.change_post')
        return False