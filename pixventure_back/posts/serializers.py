from rest_framework import serializers
from posts.models import Post
from posts.models import PostMedia
from media.models import MediaItem, MediaItemVersion
from social.utils import user_has_liked
from media.utils.media_file import get_media_file_for_display
from media.serializers import TileInfoMixin
from taxonomy.models import Term
from django.core.exceptions import ValidationError
from django.db import transaction
from main.utils import generate_unique_slug

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

    def create(self, validated_data):
        with transaction.atomic():
            request_user = self.context['request'].user

            name = validated_data.get('name')
            text = validated_data.get('text', "")
            featured_item_id = validated_data.get('featured_item')
            item_ids = validated_data.get('items', [])
            term_ids = validated_data.get('terms', [])

            # 1) Validate and load media items that belong to the user
            media_items = MediaItem.objects.filter(id__in=item_ids, owner=request_user)
            if media_items.count() != len(item_ids):
                raise ValidationError("One or more media items do not exist or do not belong to you.")

            # 2) Validate and load featured item (if provided)
            featured_item_obj = None
            if featured_item_id is not None:
                try:
                    featured_item_obj = MediaItem.objects.get(id=featured_item_id, owner=request_user)
                except MediaItem.DoesNotExist:
                    raise ValidationError("Featured item does not exist or does not belong to you.")

            # 3) Validate and load terms (if provided)
            terms_qs = Term.objects.filter(id__in=term_ids)
            if term_ids and terms_qs.count() != len(term_ids):
                raise ValidationError("One or more terms do not exist.")

            # 4) Determine main_category:
            # If user provided terms, try to use one of type 'category'
            # Otherwise, or if none of the provided terms is a category,
            # default to the first available category in the system.
            if term_ids:
                main_cat = terms_qs.filter(term_type=Term.CATEGORY).first()
                if not main_cat:
                    main_cat = Term.objects.filter(term_type=Term.CATEGORY).first()
            else:
                # No terms provided – default to a category, if one exists.
                main_cat = Term.objects.filter(term_type=Term.CATEGORY).first()

            if not main_cat:
                # If no category exists at all, raise error.
                raise ValidationError("No valid category found. Please contact support.")

            # 5) Generate a unique slug for the post
            slug = generate_unique_slug(Post, name, max_length=50)

            # 6) Create the Post object
            post = Post.objects.create(
                owner=request_user,
                name=name,
                slug=slug,
                text=text,
                featured_item=featured_item_obj,
                main_category=main_cat,
                status=Post.PENDING_MODERATION  # or use your default status
            )

            # 7) Add the terms (if any) to the post
            if term_ids:
                post.terms.add(*terms_qs)

            # 8) Create PostMedia links for each media item in the order provided
            for pos, m_id in enumerate(item_ids):
                media_obj = media_items.get(id=m_id)
                PostMedia.objects.create(
                    post=post,
                    media_item=media_obj,
                    position=pos
                )

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