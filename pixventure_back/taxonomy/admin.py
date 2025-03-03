from django.contrib import admin
from .models import Tag, Category, Term


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """
    Admin interface for the Tag model.
    """
    list_display = ('id', 'name', 'slug')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('name',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Admin interface for the Category model.
    """
    list_display = ('id', 'name', 'slug')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('name',)


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
