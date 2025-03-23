# integrations/gourl/admin.py

from django.contrib import admin
from .models import GoURLConfig


@admin.register(GoURLConfig)
class GoURLConfigAdmin(admin.ModelAdmin):
    list_display = ('coin', 'box_id', 'private_key_short')
    search_fields = ('coin', 'private_key')
    list_filter = ('coin',)
    ordering = ('coin',)

    def private_key_short(self, obj):
        return f"{obj.private_key[:10]}..." if len(obj.private_key) > 10 else obj.private_key
    private_key_short.short_description = 'Private Key'
