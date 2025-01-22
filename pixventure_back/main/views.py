from rest_framework.views import APIView
from rest_framework.response import Response
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
        return MediaItem.objects.filter(post_links__post=post).order_by('post_links__position')
    
    
class PostMediaItemDetailView(APIView):
    """
    Returns data about a single MediaItem within a specific Post, 
    along with the IDs of the previous and next items for easy navigation.
    
    URL pattern might be: /posts/<int:post_id>/items/<int:media_item_id>/
    
    Response structure (JSON):
    {
      "item_id": <int>,
      "previous_item_id": <int or null>,
      "next_item_id": <int or null>,
      "item_url": <str>
    }
    """
    permission_classes = [AllowAny]

    def get(self, request, post_id, media_item_id, *args, **kwargs):
        """
        HTTP GET method that retrieves the specified post/media item relationship
        and computes the next/previous items based on position.
        """
        # 1. Find the specific PostMedia record linking the post and media item.
        post_media = get_object_or_404(
            PostMedia,
            post_id=post_id,
            media_item_id=media_item_id
        )

        # 2. Determine the position of the current item.
        current_position = post_media.position

        # 3. Find the previous item (lowest position < current_position).
        previous_pm = (
            PostMedia.objects
            .filter(post_id=post_id, position__lt=current_position)
            .order_by('-position')
            .first()
        )
        previous_item_id = previous_pm.media_item_id if previous_pm else None

        # 4. Find the next item (lowest position > current_position).
        next_pm = (
            PostMedia.objects
            .filter(post_id=post_id, position__gt=current_position)
            .order_by('position')
            .first()
        )
        next_item_id = next_pm.media_item_id if next_pm else None

        # 5. Construct the URL for the current media item.
        #    You might use original_file, or handle logic for photos vs. videos.
        current_item = post_media.media_item
        if current_item and current_item.original_file:
            item_url = current_item.original_file.url
        else:
            item_url = ""

        # 6. Prepare the data for serialization.
        response_data = {
            "item_id": current_item.id,
            "previous_item_id": previous_item_id,
            "next_item_id": next_item_id,
            "item_url": item_url,
        }

        serializer = MediaItemInPostSerializer(data=response_data)
        serializer.is_valid(raise_exception=True)  # Validate the constructed data

        return Response(serializer.data)
