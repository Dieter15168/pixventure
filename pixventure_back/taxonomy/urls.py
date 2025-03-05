# taxonomy/urls.py

from django.urls import path
from .views import (
    AllTermsView,
    TermCreateView,
    TermDetailView,
    TermUpdateDestroyView,
)

urlpatterns = [
    # e.g. /api/terms/
    path('', AllTermsView.as_view(), name='term-list'),

    # e.g. /api/terms/new/
    path('new/', TermCreateView.as_view(), name='term-create'),

    # e.g. /api/terms/<slug>/
    path('<slug:slug>/', TermDetailView.as_view(), name='term-detail'),

    # e.g. /api/terms/<slug>/edit/
    path('<slug:slug>/edit/', TermUpdateDestroyView.as_view(), name='term-update-destroy'),
]
