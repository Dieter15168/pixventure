# albums/views.py

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404

from .models import Album, AlbumElement
from .serializers import (
    AlbumListSerializer,
    AlbumDetailSerializer,
    AlbumElementSerializer
)
from main.pagination import StandardResultsSetPagination  # your custom pagination class


class AlbumListView(generics.ListAPIView):
    """
    GET /api/albums/
    Returns a paginated list of 'public' albums using AlbumListSerializer.
    """
    serializer_class = AlbumDetailSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        # Example filter: only show PUBLIC albums
        return Album.objects.filter(status=Album.PUBLIC).order_by('-created')


class AlbumDetailView(APIView):
    """
    GET /api/albums/<pk>/
    Returns:
      - the album detail (AlbumDetailSerializer)
      - a paginated list of album elements (AlbumElementReusingSerializer),
        reusing your existing PostSerializer and MediaItemSerializer.
    """
    permission_classes = [AllowAny]

    def get(self, request, pk):
        # 1. Retrieve the album
        album = get_object_or_404(Album, pk=pk)

        # 2. Serialize album detail
        album_data = AlbumDetailSerializer(album, context={'request': request}).data

        # 3. Paginate album elements
        elements_qs = AlbumElement.objects.filter(album=album).order_by('position')
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(elements_qs, request, view=self)

        # 4. Serialize the elements, reusing the post/media logic
        elements_data = AlbumElementSerializer(
            page, many=True, context={'request': request}
        ).data

        # 5. Return combined data with pagination meta
        return Response({
            'album': album_data,
            'album_elements': elements_data,
            'count': len(elements_qs),
            'next': paginator.get_next_link(),
            'previous': paginator.get_previous_link(),
        }, status=status.HTTP_200_OK)
