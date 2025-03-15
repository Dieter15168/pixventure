# moderation/urls.py
from django.urls import path
from .views import ModerationDashboardView, ModerationActionCreateView

urlpatterns = [
    path('dashboard/', ModerationDashboardView.as_view(), name='moderation-dashboard'),
    path('action/', ModerationActionCreateView.as_view(), name='moderation-action'),
]
