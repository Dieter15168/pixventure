# posts/views.py

from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Max
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import PermissionDenied
from rest_framework import mixins

from .models import Post, PostMedia
from media.models import MediaItem
from .serializers import (
    PostSerializer,
    PostCreateSerializer,
    PostMediaItemDetailSerializer,
    PostMetaSerializer
)
from media.serializers import MediaItemSerializer
from .permissions import IsPostOwnerOrAdminOrPublicRead
from main.pagination import StandardResultsSetPagination
from taxonomy.models import Term


# 0. All public posts list
class PublicPostListView(generics.ListAPIView):
    """
    GET /api/posts/
    Returns a paginated list of 'published' posts using PostSerializer.
    
    Optionally, if you include ?slug=some-slug, returns only the matching post
    (still in a paginated results array).
    """
    serializer_class = PostSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        # Only show PUBLISHED posts
        qs = Post.objects.filter(status=Post.PUBLISHED).order_by('-published')

        # If ?slug= is provided, filter the queryset accordingly
        slug = self.request.query_params.get('slug')
        if slug:
            qs = qs.filter(slug=slug)

        return qs
    
# 1. Featured posts list (displayed on main page)
class FeaturedPostListView(generics.ListAPIView):
    """
    GET /api/posts/featured/
    Returns a paginated list of PUBLISHED + FEATURED posts using PostSerializer.
    """
    serializer_class = PostSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        # Only show PUBLISHED + is_featured_post
        qs = Post.objects.filter(status=Post.PUBLISHED, is_featured_post=True).order_by('-published')
        return qs
    

# 2. MyPostsView
class MyPostsView(generics.ListAPIView):
    """
    GET /api/posts/mine/
    Returns the current user’s posts. 
    If none exist, optionally auto-create a private "Quick save" post.
    """
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        user = self.request.user
        user_posts = Post.objects.filter(owner=user)

        return user_posts.order_by('-created')


# 3. Create new post
class PostCreateView(generics.CreateAPIView):
    """
    POST /api/posts/new/
    Creates a new post for the current user.
    """
    serializer_class = PostCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


# 4. PostDetailView
class PostDetailView(generics.RetrieveAPIView):
    """
    GET /api/posts/<pk>/
    Returns the detail of a single post using PostSerializer.
    Uses IsPostOwnerOrAdminOrPublicRead for permissions.
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsPostOwnerOrAdminOrPublicRead]
    lookup_field = "slug"


# 5. PostUpdateDestroyView
class PostUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/posts/<pk>/edit/
    PATCH /api/posts/<pk>/edit/
    DELETE /api/posts/<pk>/edit/
    For the post owner or admin.
    """
    queryset = Post.objects.all()
    serializer_class = PostCreateSerializer
    permission_classes = [IsPostOwnerOrAdminOrPublicRead]
    lookup_field = 'pk'

    def perform_destroy(self, instance):
        instance.status = Post.DELETED
        instance.save(update_fields=['status'])


# 6. PostMediaListCreateView
class PostMediaListCreateView(generics.ListCreateAPIView):
    """
    GET /api/posts/<pk>/items/
      - list media items in a post
    POST /api/posts/<pk>/items/
      - add a new media item (only owner or admin) to the post
    """
    serializer_class = MediaItemSerializer
    permission_classes = [IsPostOwnerOrAdminOrPublicRead]
    pagination_class = StandardResultsSetPagination

    def get_post(self):
        post = get_object_or_404(Post, slug=self.kwargs['slug'])
        self.check_object_permissions(self.request, post)
        return post

    def get_queryset(self):
        post = self.get_post()
        return MediaItem.objects.filter(post_links__post=post).order_by('post_links__position')

    def perform_create(self, serializer):
        """
        Instead of creating a brand new MediaItem here, 
        you can either attach an existing MediaItem to the post
        or create a new one.
        """
        post = self.get_post()
        user = self.request.user

        if (post.owner != user) and not user.is_staff:
            raise PermissionDenied("Only the post’s owner or admin can add media.")

        # If creating a brand new media item:
        media_item = serializer.save(owner=user)

        # Attach it to the post via PostMedia with next position
        max_position = PostMedia.objects.filter(post=post).aggregate(Max('position'))['position__max'] or 0
        PostMedia.objects.create(
            post=post,
            media_item=media_item,
            position=max_position + 1
        )

    def get_serializer_context(self):
        """
        Pass the post into context for blur logic, etc.
        """
        context = super().get_serializer_context()
        context['post'] = self.get_post()
        return context


# 7. PostMediaItemRetrieveDestroyView
class PostMediaItemRetrieveDestroyView(generics.GenericAPIView,
                                       mixins.RetrieveModelMixin,
                                       mixins.DestroyModelMixin):
    """
    GET /api/posts/<pk>/items/<media_item_id>/
      -> Returns details about a single MediaItem within a post,
         including prev/next item IDs and like info.

    DELETE /api/posts/<pk>/items/<media_item_id>/
      -> Removes this media item from the post. If no longer used in any other post,
         you can optionally delete it entirely.
    """
    serializer_class = PostMediaItemDetailSerializer
    permission_classes = [IsPostOwnerOrAdminOrPublicRead]

    def get_post(self):
        post_id = self.kwargs['pk']
        post = get_object_or_404(Post, pk=post_id)
        self.check_object_permissions(self.request, post)  # post-level permission
        return post

    def get_queryset(self):
        """
        The serializer references PostMedia, so let's limit queries to
        PostMedia objects associated with the given post.
        """
        post = self.get_post()
        return PostMedia.objects.filter(post=post)

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        media_item_id = self.kwargs['media_item_id']
        # We'll find the specific PostMedia entry
        post_media = get_object_or_404(queryset, media_item_id=media_item_id)
        # No separate object-level check required for post_media itself,
        # but if you had custom logic for media item ownership, do it here.
        return post_media

    def get(self, request, *args, **kwargs):
        """
        Returns full details about this specific item in the post, 
        including next/prev item IDs, likes, etc.
        """
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            context={'request': request}  # needed for blur logic, etc.
        )
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        """
        Remove this media item from the post. 
        If it's no longer used elsewhere, optionally delete the MediaItem object entirely.
        """
        post = self.get_post()
        instance = self.get_object()  # This is a PostMedia instance
        media_item = instance.media_item

        # Ensure post owner or admin
        if (post.owner != request.user) and not request.user.is_staff:
            raise PermissionDenied("Only the post’s owner or admin can remove media.")

        # 1) Remove from PostMedia
        instance.delete()

        # 2) Optionally, if the media item isn't used anywhere else, delete it.
        if not media_item.post_links.exists() and not media_item.album_elements.exists():
            media_item.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
    

 # 7. PostMetaView   
class PostMetaView(generics.RetrieveAPIView):
    """
    GET /api/posts/<pk>/meta/
    Returns minimal post meta info (name, slug, categories, tags, etc.)
    """
    queryset = Post.objects.all()
    serializer_class = PostMetaSerializer
    lookup_field = 'pk'
    
    
# 8. Retrieve post lists filtered by categories and tags
class CategoryPostsListView(generics.ListAPIView):
    """
    GET /api/categories/<slug>/posts/
    Returns a paginated list of PUBLISHED posts that have a category
    matching <slug>.
    """
    serializer_class = PostSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        category_slug = self.kwargs['slug']
        # Confirm the term actually exists
        get_object_or_404(Term, slug=category_slug, term_type=Term.CATEGORY)

        return (
            Post.objects.filter(
                status=Post.PUBLISHED,
                terms__term_type=Term.CATEGORY,
                terms__slug=category_slug
            )
            .distinct()
            .order_by('-published')
        )


class TagPostsListView(generics.ListAPIView):
    """
    GET /api/tags/<slug>/posts/
    Returns a paginated list of PUBLISHED posts that have a tag matching <slug>.
    """
    serializer_class = PostSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        tag_slug = self.kwargs['slug']
        # Confirm the term actually exists
        get_object_or_404(Term, slug=tag_slug, term_type=Term.TAG)

        return (
            Post.objects.filter(
                status=Post.PUBLISHED,
                terms__term_type=Term.TAG,
                terms__slug=tag_slug
            )
            .distinct()
            .order_by('-published')
        )
        

class MediaRedirectAPIView(APIView):
    """
    API endpoint that returns the meta information of the first published post
    associated with a given media item. The returned data includes the post's ID,
    slug, and main category slug – used to construct a redirect URL.
    """
    permission_classes = []  # AllowAny by default; adjust if needed.

    def get(self, request, media_item_id, *args, **kwargs):
        # Find a PostMedia entry where the media item is linked to a published post.
        post_media = PostMedia.objects.filter(
            media_item_id=media_item_id,
            post__status=Post.PUBLISHED
        ).select_related("post", "post__main_category").first()

        if not post_media:
            return Response(
                {"detail": "No published post associated with this media item."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        post = post_media.post
        data = {
            "post_id": post.id,
            "post_slug": post.slug,
            "main_category_slug": post.main_category.slug,
        }
        return Response(data, status=status.HTTP_200_OK)