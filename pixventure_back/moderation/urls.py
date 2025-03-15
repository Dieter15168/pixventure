# moderation/urls.py

from django.urls import path
from .views import (
    ModerationDashboardView,
    ModerationActionCreateView,
    ActiveRejectionReasonListView,
)

urlpatterns = [
    path('dashboard/', ModerationDashboardView.as_view(), name='moderation-dashboard'),
    path('action/', ModerationActionCreateView.as_view(), name='moderation-action'),
    path('rejection-reasons/', ActiveRejectionReasonListView.as_view(), name='active-rejection-reasons'),
]
