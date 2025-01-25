from django.urls import path
from .views import AlbumListView, AlbumDetailView

urlpatterns = [
    path('', AlbumListView.as_view(), name='album-list'),         # /api/albums/
    path('<int:pk>/', AlbumDetailView.as_view(), name='album-detail'),  # /api/albums/<pk>/
]
