from django.urls import path
from .views import ModerationActionView

urlpatterns = [
    path('', ModerationActionView.as_view(), name='album-list'),
]
