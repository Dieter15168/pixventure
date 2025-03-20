# media_typeviews.py

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Term
from .serializers import TermSerializer, AllTermsSerializer
from main.pagination import StandardResultsSetPagination

class AllTermsView(APIView):
    """
    GET /api/terms/
    Returns {"categories": [...], "tags": [...]} using TermSerializer
    """
    permission_classes = [AllowAny]
    def get(self, request, format=None):
        categories_qs = Term.objects.filter(term_type=2)
        tags_qs = Term.objects.filter(term_type=1)

        serializer = AllTermsSerializer({
            "categories": categories_qs,
            "tags": tags_qs
        })
        return Response(serializer.data)


class TermCreateView(generics.CreateAPIView):
    """
    POST /api/terms/new/
    Creates a new term. Client must pass 'term_type' in the payload.
    """
    serializer_class = TermSerializer
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        # We might do additional logic here if needed.
        serializer.save()


class TermDetailView(generics.RetrieveAPIView):
    """
    GET /api/terms/<slug>/
    Retrieve a term by slug. 
    Only admin can access for now.
    """
    queryset = Term.objects.all()
    serializer_class = TermSerializer
    lookup_field = 'slug'
    permission_classes = [IsAdminUser]


class TermUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/media_typeterms/<slug>/edit/
    PATCH /api/media_typeterms/<slug>/edit/
    DELETE /api/media_typeterms/<slug>/edit/
    Only admin can access for now.
    """
    queryset = Term.objects.all()
    serializer_class = TermSerializer
    lookup_field = 'slug'
    permission_classes = [IsAdminUser]
