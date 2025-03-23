# payments/admin.py

from django.contrib import admin
from django.utils.html import format_html
from .models import PaymentProvider, PaymentMethod, Transaction


@admin.register(PaymentProvider)
class PaymentProviderAdmin(admin.ModelAdmin):
    list_display = ('name', 'description_short', 'created', 'updated')
    search_fields = ('name',)
    list_filter = ('created', 'updated')
    ordering = ('-updated',)

    def description_short(self, obj):
        return (obj.description[:75] + '...') if len(obj.description) > 75 else obj.description
    description_short.short_description = 'Description'


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'provider', 'is_active', 'icon_preview', 'created', 'updated')
    search_fields = ('name', 'provider__name')
    list_filter = ('provider', 'is_active', 'created', 'updated')
    list_select_related = ('provider',)
    ordering = ('-updated',)
    readonly_fields = ('icon_preview',)

    def icon_preview(self, obj):
        if obj.icon:
            return format_html('<img src="{}" width="40" height="40" style="object-fit:contain;" />', obj.icon.url)
        return "-"
    icon_preview.short_description = 'Icon'


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'payment_method', 'amount', 'status_display',
        'is_expired', 'created_at', 'updated_at', 'expires_at'
    )
    search_fields = ('user__username', 'external_order_id')
    list_filter = ('status', 'payment_method__provider', 'created_at', 'expires_at')
    autocomplete_fields = ('user', 'payment_method')
    readonly_fields = ('created_at', 'updated_at', 'is_expired')
    ordering = ('-created_at',)

    def status_display(self, obj):
        return obj.get_status_display()
    status_display.short_description = 'Status'
