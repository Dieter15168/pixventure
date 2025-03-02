from django.contrib import admin
from .models import MediaItem, MediaItemVersion, MediaItemHash, HashType


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
    list_filter = ['status', 'item_type', 'created']
    list_select_related = ('owner',)
    raw_id_fields = ('owner',)  # Use raw id field for User model to improve performance
    inlines = [MediaItemVersionInline]
    list_per_page = 20  # Limit the number of records per page to prevent loading too many records
    
    # The `versions` field is still included, but with autocomplete and pagination
    autocomplete_fields = ['versions']  # Allow searching and selecting versions efficiently
    filter_horizontal = ('versions',)  # Display versions field with horizontal filter for selection

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

admin.site.register(MediaItem, MediaItemAdmin)
admin.site.register(MediaItemVersion, MediaItemVersionAdmin)
admin.site.register(HashType, HashTypeAdmin)
admin.site.register(MediaItemHash, MediaItemHashAdmin)
