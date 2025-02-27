# albums/views.py

import uuid
from django.shortcuts import get_object_or_404
from django.db.models import Max
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import PermissionDenied

from .models import Album, AlbumElement
from .serializers import (
    AlbumListSerializer,
    AlbumDetailSerializer,
    AlbumCreateSerializer,
    AlbumElementSerializer
)
from .permissions import IsAlbumOwnerOrAdminOrPublicRead
from .utils import generate_unique_slug
from main.pagination import StandardResultsSetPagination


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


# --- 1. MyAlbumsView ---

class MyAlbumsView(generics.ListAPIView):
    """
    GET /api/albums/mine/
    Returns current user’s albums. If none exist, auto-create
    a private "Quick save" album with a random slug (no username).
    """
    serializer_class = AlbumListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        user_albums = Album.objects.filter(owner=user)
        if not user_albums.exists():
            random_slug = f"quick-save-{uuid.uuid4().hex[:8]}"
            Album.objects.create(
                owner=user,
                name="Quick save",
                slug=random_slug,
                status=Album.PRIVATE
            )
            user_albums = Album.objects.filter(owner=user)
        return user_albums

# --- 2. AlbumCreateView ---

class AlbumCreateView(generics.CreateAPIView):
    """
    POST /api/albums/new/
    Creates a new album for the current user.
    """
    serializer_class = AlbumCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

# --- 3. AlbumDetailView (rewritten) ---

class AlbumDetailView(generics.GenericAPIView):
    """
    GET /api/albums/<slug>/
    Returns detail about the album (using AlbumDetailSerializer),
    plus a paginated list of album elements (AlbumElementSerializer).
    Uses IsAlbumOwnerOrAdminOrPublicRead for permissions.
    """
    serializer_class = AlbumDetailSerializer
    permission_classes = [IsAlbumOwnerOrAdminOrPublicRead]
    pagination_class = StandardResultsSetPagination

    def get_object(self):
        album = get_object_or_404(Album, slug=self.kwargs['slug'])
        self.check_object_permissions(self.request, album)
        return album

    def get(self, request, slug):
        album = self.get_object()

        # 1) Album detail
        album_data = self.get_serializer(album).data

        # 2) Paginated album elements
        elements_qs = AlbumElement.objects.filter(album=album).order_by('position')
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(elements_qs, request, view=self)

        elements_serializer = AlbumElementSerializer(
            page, many=True, context={'request': request}
        )
        return Response({
            'album': album_data,
            'album_elements': elements_serializer.data,
            'count': elements_qs.count(),
            'next': paginator.get_next_link(),
            'previous': paginator.get_previous_link(),
        }, status=status.HTTP_200_OK)

# --- 4. AlbumUpdateDestroyView ---

class AlbumUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/albums/<slug>/edit/
    PATCH /api/albums/<slug>/edit/
    DELETE /api/albums/<slug>/edit/
    For the album’s owner or admin. 
    You can use PATCH to rename, set to public, or archive, etc.
    DELETE for full removal if desired.
    """
    queryset = Album.objects.all()
    serializer_class = AlbumDetailSerializer
    lookup_field = 'slug'
    permission_classes = [IsAlbumOwnerOrAdminOrPublicRead]

    def perform_destroy(self, instance):
        # If you prefer archiving instead of actual delete:
        # instance.status = Album.ARCHIVED
        # instance.save()
        # Or if you want to fully delete:
        instance.delete()

# --- 5. AlbumElementsListCreateView ---

class AlbumElementsListCreateView(generics.ListCreateAPIView):
    """
    GET /api/albums/<slug>/elements/
      - list album elements (owner or public if album is public)
    POST /api/albums/<slug>/elements/
      - add a new element (only owner or admin)
    """
    serializer_class = AlbumElementSerializer
    permission_classes = [IsAlbumOwnerOrAdminOrPublicRead]
    pagination_class = StandardResultsSetPagination

    def get_album(self):
        album = get_object_or_404(Album, slug=self.kwargs['slug'])
        self.check_object_permissions(self.request, album)
        return album

    def get_queryset(self):
        album = self.get_album()
        return AlbumElement.objects.filter(album=album).order_by('position')

    def perform_create(self, serializer):
        album = self.get_album()
        # The "create" part must be restricted to owner or staff
        if (album.owner != self.request.user) and not self.request.user.is_staff:
            raise PermissionDenied("Only the owner or admin can add elements.")

        # Decide the next position automatically
        max_position = album.album_elements.aggregate(Max('position'))['position__max'] or 0
        serializer.save(album=album, position=max_position + 1)

# --- 6. AlbumElementRetrieveDestroyView ---

class AlbumElementRetrieveDestroyView(generics.RetrieveDestroyAPIView):
    """
    GET /api/albums/<slug>/elements/<int:pk>/
    DELETE /api/albums/<slug>/elements/<int:pk>/
    For the album’s owner or admin.
    """
    serializer_class = AlbumElementSerializer
    permission_classes = [IsAlbumOwnerOrAdminOrPublicRead]
    lookup_url_kwarg = 'element_id'  # or just use pk

    def get_album(self):
        album = get_object_or_404(Album, slug=self.kwargs['slug'])
        self.check_object_permissions(self.request, album)
        return album

    def get_queryset(self):
        # Return the elements for the album in question
        album = self.get_album()
        return AlbumElement.objects.filter(album=album).order_by('position')

    def perform_destroy(self, instance):
        album = self.get_album()
        if (album.owner != self.request.user) and not self.request.user.is_staff:
            raise PermissionDenied("Only the owner or admin can remove elements.")
        instance.delete()
