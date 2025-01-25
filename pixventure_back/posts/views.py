from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404

from posts.models import Post, PostMedia
from media.models import MediaItem
from .serializers import (
    PostSerializer,
    PostMediaItemDetailSerializer
)
from media.serializers import MediaItemSerializer
from main.pagination import StandardResultsSetPagination


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
        self.post = get_object_or_404(Post, pk=post_id)
        return MediaItem.objects.filter(post_links__post=self.post)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['post'] = self.post
        return context
    
    
class PostMediaItemDetailView(APIView):
    """
    Returns data about a single MediaItem within a specific Post, 
    along with the IDs of the previous and next items for navigation,
    plus like info (count and whether current user has liked it).
    
    Example endpoint: /posts/<int:post_id>/items/<int:media_item_id>/
    """
    permission_classes = [AllowAny]

    def get(self, request, post_id, media_item_id, *args, **kwargs):
        # 1. Retrieve the relevant PostMedia record
        post_media = get_object_or_404(
            PostMedia,
            post_id=post_id,
            media_item_id=media_item_id
        )

        # 2. Serialize the data
        serializer = PostMediaItemDetailSerializer(
            post_media,
            context={'request': request}  # Pass the request for 'has_liked' checks
        )
        
        # 3. Return the final JSON response
        return Response(serializer.data)