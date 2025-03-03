# taxonomy/views.py

from rest_framework import generics, status
from rest_framework.permissions import IsAdminUser
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Term
from .serializers import TermSerializer
from main.pagination import StandardResultsSetPagination

class TermListView(generics.ListAPIView):
    """
    GET /api/taxonomy/terms/
    Returns a paginated list of terms (tags + categories).
    Only admin for now, or expand with custom permissions if needed.
    """
    serializer_class = TermSerializer
    permission_classes = [IsAdminUser]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        # If you want to list all terms, or just filter by a term_type
        # e.g., ?term_type=1 for tags, ?term_type=2 for categories
        qs = Term.objects.all().order_by('name')
        term_type = self.request.GET.get('term_type')
        if term_type in ('1', '2'):
            qs = qs.filter(term_type=term_type)
        return qs


class TermCreateView(generics.CreateAPIView):
    """
    POST /api/taxonomy/terms/new/
    Creates a new term. Client must pass 'term_type' in the payload.
    """
    serializer_class = TermSerializer
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        # We might do additional logic here if needed.
        serializer.save()


class TermDetailView(generics.RetrieveAPIView):
    """
    GET /api/taxonomy/terms/<slug>/
    Retrieve a term by slug. 
    Only admin can access for now.
    """
    queryset = Term.objects.all()
    serializer_class = TermSerializer
    lookup_field = 'slug'
    permission_classes = [IsAdminUser]


class TermUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/taxonomy/terms/<slug>/edit/
    PATCH /api/taxonomy/terms/<slug>/edit/
    DELETE /api/taxonomy/terms/<slug>/edit/
    Only admin can access for now.
    """
    queryset = Term.objects.all()
    serializer_class = TermSerializer
    lookup_field = 'slug'
    permission_classes = [IsAdminUser]
