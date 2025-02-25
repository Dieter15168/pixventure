from django.contrib import admin
from .models import Album, AlbumElement
from django.utils.html import mark_safe

@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    """
    Admin interface for the Album model.
    """
    
    def featured_item_preview(self, obj):
        if obj.featured_item and obj.featured_item.thumbnail_file:
            return mark_safe(f'<img src="{obj.featured_item.thumbnail_file.url}" style="max-height: 100px;" />')
        return "No preview available"
    featured_item_preview.short_description = "Featured Item Preview"
    
    
    list_display = ('id', 'name', 'owner', 'status', 'likes_counter', 'featured_item_preview', 'created', 'updated')
    list_filter = ('status', 'created', 'updated', 'show_creator_to_others')
    search_fields = ('name', 'slug', 'owner__username')
    readonly_fields = ('created', 'updated', 'likes_counter')
    ordering = ('-created',)

    fieldsets = (
        (None, {
            'fields': ('featured_item', 'name', 'slug', 'status', 'owner', 'show_creator_to_others')
        }),
        ('Metadata', {
            'fields': ('likes_counter', 'created', 'updated'),
        }),
    )


@admin.register(AlbumElement)
class AlbumElementAdmin(admin.ModelAdmin):
    """
    Admin interface for the AlbumElement model.
    """
    list_display = (
        'id', 'album', 'element_type', 'element_post', 'element_media', 
        'position', 'created', 'updated'
    )
    list_filter = ('element_type', 'created', 'updated')
    search_fields = ('album__name', 'element_post__name', 'element_media__name')
    readonly_fields = ('created', 'updated')
    ordering = ('album', 'position')

    fieldsets = (
        (None, {
            'fields': ('album', 'element_type', 'element_post', 'element_media', 'position')
        }),
        ('Metadata', {
            'fields': ('created', 'updated'),
        }),
    )
