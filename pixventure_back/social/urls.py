from django.urls import path
from .views import LikeToggleAPIView

urlpatterns = [
    path('like-toggle/', LikeToggleAPIView.as_view(), name='like-toggle'),
]
