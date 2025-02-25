from django.contrib import admin
from .models import Like


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    """
    Admin interface for the Like model.
    """
    list_display = ('id', 'user', 'post', 'media_item', 'album', 'created')
    list_filter = ('created',)
    search_fields = ('user__username', 'post__name', 'media_item__original_filename')
    readonly_fields = ('created',)
    ordering = ('-created',)
    fieldsets = (
        (None, {
            'fields': ('user', 'post', 'media_item', 'album')
        }),
        ('Metadata', {
            'fields': ('created',),
        }),
    )
