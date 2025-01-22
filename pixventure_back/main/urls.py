from django.urls import path
from .views import PostListView, PostDetailView, PostMediaListView, PostMediaItemDetailView

urlpatterns = [
    path('posts/', PostListView.as_view(), name='post-list'),
    path('posts/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('posts/<int:pk>/items/', PostMediaListView.as_view(), name='post-items-list'),
    path('posts/<int:post_id>/items/<int:media_item_id>/', PostMediaItemDetailView.as_view(), name='post-item-detail'),
]
