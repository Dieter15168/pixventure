# albums/urls.py

from django.urls import path
from .views import (
    AlbumListView,           # existing public list (only PUBLIC albums)
    MyAlbumsView,
    AlbumCreateView,
    AlbumDetailView,
    AlbumUpdateDestroyView,
    AlbumElementsListCreateView,
    AlbumElementRetrieveDestroyView,
)

urlpatterns = [
    # Existing (public) album listing: /api/albums/
    path('', AlbumListView.as_view(), name='album-list'),

    # My albums: /api/albums/mine/
    path('mine/', MyAlbumsView.as_view(), name='my-albums'),

    # Create new album: /api/albums/new/
    path('new/', AlbumCreateView.as_view(), name='create-album'),

    # Album detail: /api/albums/<slug>/
    path('<str:slug>/', AlbumDetailView.as_view(), name='album-detail'),

    # Edit/delete album: /api/albums/<slug>/edit/
    path('<str:slug>/edit/', AlbumUpdateDestroyView.as_view(), name='edit-album'),

    # Album elements listing/creation: /api/albums/<slug>/elements/
    path('<str:slug>/elements/', AlbumElementsListCreateView.as_view(), name='album-elements-list-create'),

    # Retrieve/delete a specific element: /api/albums/<slug>/elements/<int:element_id>/
    path('<str:slug>/elements/<int:element_id>/', AlbumElementRetrieveDestroyView.as_view(), name='album-element-detail'),
]
