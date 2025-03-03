# posts/urls.py

from django.urls import path
from .views import (
    PublicPostListView,
    MyPostsView,
    PostCreateView,
    PostDetailView,
    PostUpdateDestroyView,
    PostMediaListCreateView,
    PostMediaItemRetrieveDestroyView,
)

urlpatterns = [
    # 1. Public posts list
    path('', PublicPostListView.as_view(), name='post-public-list'),

    # 2. My posts (if you want to replicate the auto-create logic)
    path('mine/', MyPostsView.as_view(), name='my-posts'),

    # 3. Create new post
    path('new/', PostCreateView.as_view(), name='create-post'),

    # 4. Post detail
    path('<int:pk>/', PostDetailView.as_view(), name='post-detail'),

    # 5. Edit/delete post
    path('<int:pk>/edit/', PostUpdateDestroyView.as_view(), name='post-edit'),

    # 6. List / create post media items
    path('<int:pk>/items/', PostMediaListCreateView.as_view(), name='post-items-list-create'),

    # 7. Retrieve / delete a specific media item within a post
    path('<int:pk>/items/<int:media_item_id>/', PostMediaItemRetrieveDestroyView.as_view(), name='post-item-retrieve-destroy'),
]
