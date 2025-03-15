# mainapp/admin.py
from django.contrib import admin
from .models import Setting

@admin.register(Setting)
class SettingAdmin(admin.ModelAdmin):
    """
    Django Admin configuration for the Setting model.
    Provides better usability with search, filtering, and inline editing.
    """
    list_display = ("key", "value")
    search_fields = ("key", "value")
    list_editable = ("value",)
    list_per_page = 20
