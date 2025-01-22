from django.contrib import admin
from .models import MediaItem, MediaItemHash


@admin.register(MediaItem)
class MediaItemAdmin(admin.ModelAdmin):
    """
    Admin interface for the MediaItem model.
    """
    list_display = (
        'id', 'item_type', 'status', 'original_filename', 
        'file_format', 'owner', 'likes_counter', 'created', 'updated'
    )
    list_filter = ('status', 'item_type', 'created', 'updated')
    search_fields = ('original_filename', 'owner__username')
    readonly_fields = ('created', 'updated', 'likes_counter')
    ordering = ('-created',)

    fieldsets = (
        (None, {
            'fields': (
                'status', 'item_type', 'original_filename', 
                'file_format', 'owner'
            )
        }),
        ('Files', {
            'fields': (
                'original_file', 'watermarked_file', 'preview_file', 'blurred_preview_file', 
                'thumbnail_file', 'blurred_thumbnail_file'
            ),
        }),
        ('Metadata', {
            'fields': ('width', 'height', 'file_size', 'is_renamed', 'likes_counter', 'created', 'updated'),
        }),
    )


@admin.register(MediaItemHash)
class MediaItemHashAdmin(admin.ModelAdmin):
    """
    Admin interface for the MediaItemHash model.
    """
    list_display = (
        'id', 'media_item', 'sha256', 'a_hash', 'p_hash', 
        'd_hash', 'w_hash', 'crop_resistant_hash', 'color_hash'
    )
    list_filter = ('media_item__item_type',)
    search_fields = ('media_item__original_filename', 'sha256', 'a_hash', 'p_hash')
    ordering = ('media_item',)

    fieldsets = (
        (None, {
            'fields': ('media_item',)
        }),
        ('Hashes', {
            'fields': ('sha256', 'a_hash', 'p_hash', 'd_hash', 'w_hash', 'crop_resistant_hash', 'color_hash'),
        }),
    )
