# integrations/gourl/admin.py

from django.contrib import admin
from .models import GoURLConfig, PaymentCallbackLog


@admin.register(GoURLConfig)
class GoURLConfigAdmin(admin.ModelAdmin):
    list_display = ('coin', 'box_id', 'private_key_short')
    search_fields = ('coin', 'private_key')
    list_filter = ('coin',)
    ordering = ('coin',)

    def private_key_short(self, obj):
        return f"{obj.private_key[:10]}..." if len(obj.private_key) > 10 else obj.private_key
    private_key_short.short_description = 'Private Key'


@admin.register(PaymentCallbackLog)
class PaymentCallbackLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'transaction', 'user', 'status', 'confirmed', 'created_at')
    list_filter = ('status', 'confirmed', 'created_at')
    search_fields = ('transaction__id', 'user__username', 'user__email')
    ordering = ('-created_at',)
    readonly_fields = ('raw_data', 'created_at')
