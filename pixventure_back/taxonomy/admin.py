from django.contrib import admin
from .models import Term


@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    """
    Admin interface for the Term model (Tags & Categories).
    """

    list_display = ('id', 'name', 'term_type', 'slug')
    list_filter = ('term_type',)  # Allows filtering by type (Tags vs. Categories)
    search_fields = ('name', 'slug')
    ordering = ('term_type', 'name')

    # Ensure autocomplete works when selecting terms elsewhere in admin
    autocomplete_fields = []

    fieldsets = (
        (None, {
            'fields': ('term_type', 'name', 'slug')
        }),
    )
