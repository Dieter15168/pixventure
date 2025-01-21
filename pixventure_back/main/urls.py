from django.urls import path
from .views import PostListView, PostDetailView, PostMediaListView

urlpatterns = [
    path('posts/', PostListView.as_view(), name='post-list'),
    path('posts/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('posts/<int:pk>/items/', PostMediaListView.as_view(), name='post-items-list'),
]
