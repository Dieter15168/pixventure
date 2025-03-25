# posts/urls.py

from django.urls import path
from .views import (
    PublicPostListView,
    FeaturedPostListView,
    MyPostsView,
    PostCreateView,
    PostDetailView,
    PostUpdateDestroyView,
    PostMediaListCreateView,
    PostMediaItemRetrieveDestroyView,
    PostMetaView,
    CategoryPostsListView,
    TagPostsListView,
    MediaRedirectAPIView,
)

urlpatterns = [
    # 1. Public posts list
    path('', PublicPostListView.as_view(), name='post-public-list'),
    
    path("featured/", FeaturedPostListView.as_view(), name="featured-posts-list"),

    # 2. My posts (if you want to replicate the auto-create logic)
    path('mine/', MyPostsView.as_view(), name='my-posts'),

    # 3. Create new post
    path('new/', PostCreateView.as_view(), name='create-post'),

    # 4. Post detail
    path('<int:pk>/', PostDetailView.as_view(), name='post-detail'),

    # 5. Edit/delete post
    path('<int:pk>/edit/', PostUpdateDestroyView.as_view(), name='post-edit'),

    # 6. List / create post media items
    path("<slug:slug>/items/", PostMediaListCreateView.as_view(), name="post-items-list-create"),

    # 7. Retrieve / delete a specific media item within a post
    path('<int:pk>/items/<int:media_item_id>/', PostMediaItemRetrieveDestroyView.as_view(), name='post-item-retrieve-destroy'),
    
    # 8. Retrieve post meta
    path('<int:pk>/meta/', PostMetaView.as_view(), name='post-meta'),
    
    # 9. Retrieve post lists filtered by categories and tags
    path("categories/<slug:slug>/", CategoryPostsListView.as_view(), name="category-posts-list"),
    path("tags/<slug:slug>/", TagPostsListView.as_view(), name="tag-posts-list"),
    
    # 10. Retrieve context necessary for the media redirect page necessary to navigate from item id to view post item page
    path("redirect/<int:media_item_id>/", MediaRedirectAPIView.as_view(), name="media-redirect"),
]
