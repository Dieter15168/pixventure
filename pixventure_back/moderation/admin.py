from django.contrib import admin
from .models import RejectionReason, ModerationAction

@admin.register(RejectionReason)
class RejectionReasonAdmin(admin.ModelAdmin):
    list_display = ("order", "name", "is_active")
    list_display_links = ("name",)  # Ensure 'order' is editable
    list_editable = ("is_active", "order")  # 'order' is now allowed in list_editable
    search_fields = ("name", "description")
    list_filter = ("is_active",)
    ordering = ("order",)

@admin.register(ModerationAction)
class ModerationActionAdmin(admin.ModelAdmin):
    list_display = (
        "performed_at", "moderator", "owner", "post", "media_item", 
        "old_status", "new_status", "rejection_reason"
    )
    list_filter = ("performed_at", "new_status", "rejection_reason")
    search_fields = ("moderator__username", "owner__username", "comment")
    readonly_fields = ("performed_at",)
    autocomplete_fields = ("post", "media_item", "moderator", "owner", "rejection_reason")
