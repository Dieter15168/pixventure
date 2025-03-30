from rest_framework import serializers
from django.db import transaction
from posts.models import Post
from posts.models import PostMedia
from media.models import MediaItem, MediaItemVersion
from social.utils import user_has_liked
from memberships.utils import check_if_user_is_paying
from media.utils.media_file import get_media_file_for_display, get_media_display_info, is_media_locked
from media.serializers import TileInfoMixin
from taxonomy.models import Term
from django.core.exceptions import ValidationError
from posts.managers.post_creation_manager import PostCreationManager

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
    locked = serializers.SerializerMethodField()
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    main_category_slug = serializers.SerializerMethodField()


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
            'locked',
            'owner_username',
            'tile_size',
            'main_category_slug',
        ]

    def get_images_count(self, obj):
        # Query PostMedia for this post, counting items that are PHOTOS
        return obj.post_media_links.filter(media_item__media_type=MediaItem.PHOTO).count()

    def get_videos_count(self, obj):
        # Query PostMedia for this post, counting items that are VIDEOS
        return obj.post_media_links.filter(media_item__media_type=MediaItem.VIDEO).count()

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
        
    def get_locked(self, obj):
        """
        Determines whether the featured media item is locked (i.e., a blurred version is served).
        """
        request = self.context.get('request')
        user = request.user if request else None
        featured = obj.featured_item
        if not featured:
            return False
        return is_media_locked(featured, user, post=obj)
        
    # TileInfoMixin's required method:
    def get_featured_image_dimensions(self, obj):
        # We assume that the Post has a featured_item field (a MediaItem)
        if not obj.featured_item:
            return None
        thumbnail = obj.featured_item.versions.filter(version_type=MediaItemVersion.THUMBNAIL).first()
        if thumbnail and thumbnail.width and thumbnail.height:
            return (thumbnail.width, thumbnail.height)
        return None
    
    def get_main_category_slug(self, obj):
        if obj.main_category:
            return obj.main_category.slug
        return None
    
    
class MyPostSerializer(PostSerializer):
    """
    Owner-facing serializer for a Post, extends the public serializer
    by adding `status` (and potentially other user-only fields).
    """
    status = serializers.SerializerMethodField()

    class Meta(PostSerializer.Meta):
        fields = PostSerializer.Meta.fields + ['status']

    def get_status(self, obj):
        # Return the human-readable status.
        return obj.get_status_display()


class PostMediaItemDetailSerializer(serializers.ModelSerializer):
    """
    Serializes a single PostMedia object for the item viewer, returning:
      item_id,
      likes_counter,
      has_liked,
      previous_item_id,
      next_item_id,
      item_url,
      served_width,
      served_height,
      original_width,
      original_height,
      show_membership_prompt,
      locked,
      media_type,
      video_poster_url
    """

    item_id = serializers.SerializerMethodField()
    likes_counter = serializers.SerializerMethodField()
    has_liked = serializers.SerializerMethodField()
    previous_item_id = serializers.SerializerMethodField()
    next_item_id = serializers.SerializerMethodField()
    item_url = serializers.SerializerMethodField()
    served_width = serializers.SerializerMethodField()
    served_height = serializers.SerializerMethodField()
    original_width = serializers.SerializerMethodField()
    original_height = serializers.SerializerMethodField()
    show_membership_prompt = serializers.SerializerMethodField()
    locked = serializers.SerializerMethodField()
    media_type = serializers.SerializerMethodField()
    video_poster_url = serializers.SerializerMethodField()

    class Meta:
        model = PostMedia
        fields = [
            'item_id',
            'likes_counter',
            'has_liked',
            'previous_item_id',
            'next_item_id',
            'item_url',
            'served_width',
            'served_height',
            'original_width',
            'original_height',
            'show_membership_prompt',
            'locked',
            'media_type',
            'video_poster_url',
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

    def _get_display_info(self, obj):
        """
        Returns (chosen_version, chosen_url) for this media item.
        We cache it in serializer context to avoid multiple queries.
        """
        cache_key = f"postmedia_item_{obj.pk}_info"
        if cache_key not in self.context:
            request = self.context.get('request')
            user = request.user if request else None

            chosen_version, chosen_url = get_media_display_info(
                media_item=obj.media_item,
                user=user,
                post=obj.post,
                thumbnail=False  # or True if you're serving "thumbnail" in this endpoint
            )
            self.context[cache_key] = (chosen_version, chosen_url)
        return self.context[cache_key]

    def get_item_url(self, obj):
        """The final URL. Pulled from the chosen version's info."""
        chosen_version, chosen_url = self._get_display_info(obj)
        return chosen_url

    def get_served_width(self, obj):
        chosen_version, _ = self._get_display_info(obj)
        return chosen_version.width if chosen_version and chosen_version.width else None

    def get_served_height(self, obj):
        chosen_version, _ = self._get_display_info(obj)
        return chosen_version.height if chosen_version and chosen_version.height else None

    def get_original_width(self, obj):
        original = obj.media_item.versions.filter(version_type=MediaItemVersion.ORIGINAL).first()
        return original.width if original and original.width else None

    def get_original_height(self, obj):
        original = obj.media_item.versions.filter(version_type=MediaItemVersion.ORIGINAL).first()
        return original.height if original and original.height else None

    def get_show_membership_prompt(self, obj):
        """
        True if the served version is 'smaller' than the original
        and is some kind of preview/blurred preview (i.e. for non-paying user).
        Adapt the condition as you see fit.
        """
        chosen_version, _ = self._get_display_info(obj)
        if not chosen_version:
            return False

        if chosen_version.version_type in [
            MediaItemVersion.PREVIEW,
            MediaItemVersion.BLURRED_PREVIEW,
            # possibly THUMBNAIL, etc., if you want the prompt for them too
        ]:
            original = obj.media_item.versions.filter(version_type=MediaItemVersion.ORIGINAL).first()
            if not original:
                return False

            served_w = chosen_version.width or 0
            served_h = chosen_version.height or 0
            orig_w = original.width or 0
            orig_h = original.height or 0

            # If either dimension is smaller, we consider it "lower-res"
            if served_w < orig_w or served_h < orig_h:
                return True

        return False

    def get_locked(self, obj):
        """
        Use is_media_locked to see if the item is locked for this user.
        """
        request = self.context.get('request')
        user = request.user if request else None
        return is_media_locked(obj.media_item, user, post=obj.post)

    def get_media_type(self, obj):
        """Returns the media type as a string, e.g. 'photo' or 'video'."""
        return obj.media_item.get_media_type_display().lower()

    def get_video_poster_url(self, obj):
        """
        If the media is a video, return a URL to the thumbnail/poster version.
        Otherwise return None.
        """
        if obj.media_item.media_type != MediaItem.VIDEO:
            return None

        # For example, assume there is a 'THUMBNAIL' version type you use as a poster
        thumbnail_version = obj.media_item.versions.filter(
            version_type=MediaItemVersion.THUMBNAIL
        ).first()

        # If a thumbnail version exists, return its URL; otherwise None
        if thumbnail_version and thumbnail_version.file:
            return thumbnail_version.file.url

        return None


class PostCreateSerializer(serializers.Serializer):
    """
    For creating a new post with a payload like:
    {
      "name": "Some new test post",
      "featured_item": 28,
      "items": [29, 28],
      "terms": [3, 2],    // Optional: may be an empty list
      "text": "Some optional text..."
    }
    """
    name = serializers.CharField(max_length=1024)
    text = serializers.CharField(required=False, allow_blank=True)
    featured_item = serializers.IntegerField(required=False, allow_null=True)
    items = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False
    )
    terms = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=True
    )

    @transaction.atomic
    def create(self, validated_data):
        request_user = self.context['request'].user
        # Defer all logic to PostCreationManager
        try:
            post = PostCreationManager.create_post(validated_data, request_user)
        except ValueError as e:
            # Convert ValueError to DRF ValidationError for proper error response
            raise serializers.ValidationError(str(e))
        return post

    def to_representation(self, instance):
        return {
            "id": instance.id,
            "name": instance.name,
            "slug": instance.slug,
            "featured_item_id": instance.featured_item.id if instance.featured_item else None,
            "terms": list(instance.terms.values_list('id', flat=True)),
            "items": list(instance.post_media_links.values_list('media_item_id', flat=True)),
            "owner_id": instance.owner_id
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
        queryset = obj.terms.filter(term_type=Term.CATEGORY)
        return TermSerializer(queryset, many=True).data

    def get_tags(self, obj):
        from taxonomy.serializers import TermSerializer
        queryset = obj.terms.filter(term_type=Term.TAG)
        return TermSerializer(queryset, many=True).data

    def get_can_edit(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            # Example logic: user can edit if they own the post or have the change permission.
            return obj.owner == request.user or request.user.has_perm('posts.change_post')
        return False