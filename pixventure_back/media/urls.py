# media/urls.py

from django.urls import path
from .views import (
    MediaItemCreateView,
    MediaItemDeleteView,
    MediaItemListView,
    MediaItemDetailView,
    MediaItemAvailableForPostView,
    RandomMediaItemView,
)

urlpatterns = [
    # List all media items
    path('', MediaItemListView.as_view(), name='media-item-list'),
    
    # Create a new media item
    path('new/', MediaItemCreateView.as_view(), name='media-item-create'),
    
    # View details of a specific media item
    path('<int:pk>/', MediaItemDetailView.as_view(), name='media-item-detail'),
    
    # Delete a media item
    path('<int:pk>/delete/', MediaItemDeleteView.as_view(), name='media-item-delete'),
    
    # Get unpublished items that are available for creating a post
    path('unpublished/', MediaItemAvailableForPostView.as_view(), name='media-item-available'),
    
    # New endpoint for random media items
    path('random/', RandomMediaItemView.as_view(), name='media-item-random'),
]
