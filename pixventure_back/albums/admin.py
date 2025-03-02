from django.contrib import admin
from django.utils.html import mark_safe
from .models import Album, AlbumElement
from media.models import MediaItemVersion
from posts.models import Post

class AlbumElementInline(admin.TabularInline):
    """
    Inline admin for AlbumElement. This allows you to manage the media items in the album.
    """
    model = AlbumElement
    extra = 1
    fields = ['element_type', 'element_post', 'element_media', 'position', 'element_media_preview']
    readonly_fields = ['element_media_preview']
    ordering = ('position',)

    def element_media_preview(self, obj):
        """
        Display the thumbnail for the media element.
        """
        if obj.element_type == AlbumElement.MEDIA_TYPE and obj.element_media:
            # Retrieve the thumbnail version of the media item
            thumbnail_version = obj.element_media.versions.filter(version_type=MediaItemVersion.THUMBNAIL).first()
            if thumbnail_version and thumbnail_version.file:
                return mark_safe(f'<img src="{thumbnail_version.file.url}" style="max-height: 50px;" />')
        return "No thumbnail available"
    
    element_media_preview.short_description = "Media Thumbnail"

@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    """
    Admin interface for the Album model.
    """

    def featured_item_preview(self, obj):
        """
        Display the thumbnail for the featured item.
        """
        if obj.featured_item:
            # Retrieve the thumbnail version of the featured item
            thumbnail_version = obj.featured_item.versions.filter(version_type=MediaItemVersion.THUMBNAIL).first()
            if thumbnail_version and thumbnail_version.file:
                return mark_safe(f'<img src="{thumbnail_version.file.url}" style="max-height: 100px;" />')
        return "No preview available"
    
    featured_item_preview.short_description = "Featured Item Preview"

    list_display = (
        'id', 'name', 'owner', 'status', 'likes_counter', 
        'featured_item_preview', 'created', 'updated'
    )
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
    inlines = [AlbumElementInline]  # Add AlbumElementInline for handling Album elements


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
