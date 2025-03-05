# posts/admin.py

from django import forms
from django.contrib import admin
from django.utils.html import mark_safe
from .models import Post, PostMedia
from media.models import MediaItemVersion
from taxonomy.models import Term

class PostAdminForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        """
        Restrict the main_category queryset to only categories,
        and the tags queryset to only tags.
        """
        super().__init__(*args, **kwargs)
        # 2 => CATEGORY
        self.fields['main_category'].queryset = Term.objects.filter(term_type=2)
        # 2 => CATEGORY
        self.fields['categories'].queryset = Term.objects.filter(term_type=2)
        # 1 => TAG
        self.fields['tags'].queryset = Term.objects.filter(term_type=1)

class PostMediaInline(admin.TabularInline):
    """
    Inline admin for the PostMedia model, which connects Post to MediaItems.
    Displays a thumbnail for each media item and allows for reordering.
    """
    model = PostMedia
    extra = 1
    fields = ['media_item', 'position', 'media_item_preview']
    readonly_fields = ['media_item_preview']
    ordering = ('position',)

    def media_item_preview(self, obj):
        if obj.media_item:
            thumbnail_version = obj.media_item.versions.filter(version_type=MediaItemVersion.THUMBNAIL).first()
            if thumbnail_version and thumbnail_version.file:
                return mark_safe(f'<img src="{thumbnail_version.file.url}" style="max-height: 50px;" />')
        return "No thumbnail available"
    
    media_item_preview.short_description = "Thumbnail"

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """
    Admin interface for the Post model.
    """
    form = PostAdminForm  # Use the custom form

    def featured_item_preview(self, obj):
        if obj.featured_item:
            thumbnail_version = obj.featured_item.versions.filter(version_type=MediaItemVersion.THUMBNAIL).first()
            if thumbnail_version and thumbnail_version.file:
                return mark_safe(f'<img src="{thumbnail_version.file.url}" style="max-height: 100px;" />')
        return "No preview available"

    featured_item_preview.short_description = "Featured Item Preview"

    list_display = (
        'id', 'name', 'owner', 'status', 'main_category',
        'is_featured_post', 'likes_counter', 'created', 'updated',
        'featured_item_preview', 'is_blurred'
    )
    list_filter = ('status', 'main_category', 'is_featured_post', 'created', 'updated')
    search_fields = ('name', 'slug', 'owner__username', 'main_category__name')
    readonly_fields = ('created', 'updated', 'likes_counter')
    ordering = ('-created',)
    fieldsets = (
        (None, {
            'fields': (
                'name', 'slug', 'status', 'text', 'owner', 
                'main_category', 'categories', 'tags', 'featured_item', 'is_featured_post', 'is_blurred'
            )
        }),
        ('Metadata', {
            'fields': ('likes_counter', 'created', 'updated'),
        }),
    )
    filter_horizontal = ('categories', 'tags',)
    inlines = [PostMediaInline]


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
