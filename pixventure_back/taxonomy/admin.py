from django.contrib import admin
from .models import Tag, Category


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
