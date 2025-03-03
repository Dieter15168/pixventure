# taxonomy/urls.py

from django.urls import path
from .views import (
    TermListView,
    TermCreateView,
    TermDetailView,
    TermUpdateDestroyView,
)

urlpatterns = [
    # e.g. /api/taxonomy/terms/
    path('', TermListView.as_view(), name='term-list'),

    # e.g. /api/taxonomy/terms/new/
    path('new/', TermCreateView.as_view(), name='term-create'),

    # e.g. /api/taxonomy/terms/<slug>/
    path('<slug:slug>/', TermDetailView.as_view(), name='term-detail'),

    # e.g. /api/taxonomy/terms/<slug>/edit/
    path('<slug:slug>/edit/', TermUpdateDestroyView.as_view(), name='term-update-destroy'),
]
