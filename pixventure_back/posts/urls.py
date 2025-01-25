from django.urls import path
from .views import PostListView, PostDetailView, PostMediaListView, PostMediaItemDetailView

urlpatterns = [
    path('', PostListView.as_view(), name='post-list'),
    path('<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('<int:pk>/items/', PostMediaListView.as_view(), name='post-items-list'),
    path('<int:post_id>/items/<int:media_item_id>/', PostMediaItemDetailView.as_view(), name='post-item-detail'),
]
