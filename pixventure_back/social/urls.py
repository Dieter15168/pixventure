from django.urls import path
from .views import LikeToggleAPIView

urlpatterns = [
    path('like/', LikeToggleAPIView.as_view(), name='like'),
]
