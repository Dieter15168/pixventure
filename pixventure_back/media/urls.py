# media/urls.py

from django.urls import path
from .views import (
    MediaItemCreateView,
    MediaItemDeleteView,
    MediaItemListView,
    MediaItemDetailView
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
]
