# search/urls.py
from django.urls import path
from .views import BasicSearchView

urlpatterns = [
    # Basic search endpoint: /api/search/?q=...
    path('', BasicSearchView.as_view(), name='search-basic'),
]
