# search/views.py
from rest_framework import generics
from rest_framework.permissions import AllowAny
from django.db.models import Q
from posts.models import Post
from posts.serializers import PostSerializer
from main.pagination import StandardResultsSetPagination

class BasicSearchView(generics.ListAPIView):
    """
    Basic Search API Endpoint

    GET parameters:
      - q: The search query string to match against post name and text.
      - page: Pagination parameter for page number (handled by pagination).

    This view returns a paginated list of published posts that match the search query.
    """
    serializer_class = PostSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        queryset = Post.objects.filter(status=Post.PUBLISHED)
        if query:
            # Filter posts where the name or text contains the search query (case insensitive)
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(text__icontains=query)
            )
        # Order by published date descending and optimize related lookups
        return queryset.order_by('-published').select_related('owner', 'main_category')
