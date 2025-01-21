from rest_framework import generics
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404

from posts.models import Post, PostMedia  # if you have a through-model named PostMedia
from media.models import MediaItem
from .serializers import (
    PostSerializer,
    MediaItemSerializer,
    MediaItemInPostSerializer
)
from .pagination import StandardResultsSetPagination


class PostListView(generics.ListAPIView):
    """
    GET /api/posts/
    Returns a paginated list of posts, using PostSerializer.
    """
    serializer_class = PostSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        # Example: only show PUBLISHED posts
        return Post.objects.filter(status=Post.PUBLISHED).order_by('-created')


class PostDetailView(generics.RetrieveAPIView):
    """
    GET /api/posts/<pk>/
    Returns the detail of a single post using PostSerializer.
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [AllowAny]
    lookup_field = 'pk'


class PostMediaListView(generics.ListAPIView):
    """
    GET /api/posts/<pk>/items/
    Returns a paginated list of media items in a given post.
    For each item, we use the standard MediaItemSerializer (or a custom approach).
    
    If you need prev/next logic, you could either:
      - incorporate it into the serializer
      - or handle it in a custom method below
    """
    serializer_class = MediaItemSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        post_id = self.kwargs['pk']
        post = get_object_or_404(Post, pk=post_id)
        # Example if you have M2M with a through-model 'PostMedia'
        # or if it's a direct M2M. We'll assume a through model named "PostMedia" with .media_item
        return MediaItem.objects.filter(post_links__post=post).order_by('post_links__position')
        # Alternatively:
        # return post.media_items.all().order_by(...) if you don't rely on a separate position field
