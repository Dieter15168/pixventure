from django.contrib import admin
from .models import Post, PostMedia
from django.utils.html import mark_safe


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """
    Admin interface for the Post model.
    """
    
    def featured_item_preview(self, obj):
        if obj.featured_item and obj.featured_item.thumbnail_file:
            return mark_safe(f'<img src="{obj.featured_item.thumbnail_file.url}" style="max-height: 100px;" />')
        return "No preview available"
    featured_item_preview.short_description = "Featured Item Preview"


    list_display = (
        'id', 'name', 'owner', 'status', 'main_category', 
        'is_featured_post', 'likes_counter', 'created', 'updated', 'featured_item_preview', 'is_blurred'
    )
    list_filter = ('status', 'main_category', 'is_featured_post', 'created', 'updated')
    search_fields = ('name', 'slug', 'owner__username', 'main_category__name')
    readonly_fields = ('created', 'updated', 'likes_counter')
    ordering = ('-created',)

    fieldsets = (
        (None, {
            'fields': (
                'name', 'slug', 'status', 'text', 'owner', 
                'main_category', 'tags', 'featured_item', 'is_featured_post', 'is_blurred'
            )
        }),
        ('Metadata', {
            'fields': ('likes_counter', 'created', 'updated'),
        }),
    )
    filter_horizontal = ('tags',)


@admin.register(PostMedia)
class PostMediaAdmin(admin.ModelAdmin):
    """
    Admin interface for the PostMedia model.
    """
    list_display = (
        'id', 'post', 'media_item', 'position', 'added', 'updated'
    )
    list_filter = ('post', 'added', 'updated')
    search_fields = ('post__name', 'media_item__original_filename')
    readonly_fields = ('added', 'updated')
    ordering = ('post', 'position')

    fieldsets = (
        (None, {
            'fields': ('post', 'media_item', 'position')
        }),
        ('Metadata', {
            'fields': ('added', 'updated'),
        }),
    )
