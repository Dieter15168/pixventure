from django.contrib import admin
from .models import MediaItem, MediaItemVersion, MediaItemHash, HashType, DuplicateCase


class MediaItemHashInline(admin.TabularInline):
    model = MediaItemHash
    extra = 1
    fields = ['hash_type', 'hash_value']
    raw_id_fields = ('media_item_version',)
    autocomplete_fields = ['hash_type']
    show_change_link = True


class MediaItemVersionInline(admin.TabularInline):
    """
    Inline admin for MediaItemVersion. This allows you to link versions to a media item.
    """
    model = MediaItemVersion
    extra = 1
    fields = ['version_type', 'file', 'width', 'height', 'file_size']
    raw_id_fields = ('media_item',)  # Use raw id for media_item to improve performance
    autocomplete_fields = ['media_item']  # Enable autocomplete to search for media_item
    show_change_link = True
    list_per_page = 20  # Limit the number of versions displayed per page

class MediaItemAdmin(admin.ModelAdmin):
    """
    Admin interface for the MediaItem model.
    """
    list_display = ['id', 'original_filename', 'status', 'created', 'updated']
    search_fields = ['original_filename', 'owner__username']
    list_filter = ['status', 'media_type', 'created']
    list_select_related = ('owner',)
    raw_id_fields = ('owner',)  # Use raw id field for User model to improve performance
    inlines = [MediaItemVersionInline]
    list_per_page = 20  # Limit the number of records per page to prevent loading too many records

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        # Ensure versions field is available in the form but managed efficiently
        return fieldsets


class MediaItemVersionAdmin(admin.ModelAdmin):
    list_display = ['media_item', 'get_version_type_display', 'file', 'width', 'height', 'file_size']
    list_filter = ['version_type', 'created']
    search_fields = ['media_item__original_filename', 'media_item__owner__username']
    raw_id_fields = ('media_item',)  # Reduce queries when selecting related MediaItem
    list_select_related = ('media_item',)
    inlines = [MediaItemHashInline]  # Inline for MediaItemHash related to the version
    list_per_page = 20  # Keep pagination to avoid query overload


class HashTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created', 'updated']
    search_fields = ['name']
    list_per_page = 20


class MediaItemHashAdmin(admin.ModelAdmin):
    list_display = ['media_item_version', 'hash_type', 'hash_value', 'created', 'updated']
    list_filter = ['hash_type']
    raw_id_fields = ('media_item_version', 'hash_type')
    list_select_related = ('media_item_version', 'hash_type')
    list_per_page = 20


@admin.register(DuplicateCase)
class DuplicateCaseAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'candidate_link',
        'duplicate_link',
        'confidence_score',
        'status_display',
        'created',
        'updated',
    )
    list_filter = ('status', 'created', 'updated')
    search_fields = (
        'candidate__id',
        'duplicate__id',
        'candidate__original_filename',  # if you have a filename or title field on MediaItem
        'duplicate__original_filename',
    )
    readonly_fields = ('created', 'updated')
    ordering = ('-created',)

    def status_display(self, obj):
        return obj.get_status_display()
    status_display.short_description = 'Status'

    def candidate_link(self, obj):
        return f'<a href="/admin/media/mediaitem/{obj.candidate.id}/change/">{obj.candidate.id}</a>'
    candidate_link.short_description = 'Candidate'
    candidate_link.allow_tags = True

    def duplicate_link(self, obj):
        return f'<a href="/admin/media/mediaitem/{obj.duplicate.id}/change/">{obj.duplicate.id}</a>'
    duplicate_link.short_description = 'Duplicate'
    duplicate_link.allow_tags = True


admin.site.register(MediaItem, MediaItemAdmin)
admin.site.register(MediaItemVersion, MediaItemVersionAdmin)
admin.site.register(HashType, HashTypeAdmin)
admin.site.register(MediaItemHash, MediaItemHashAdmin)
