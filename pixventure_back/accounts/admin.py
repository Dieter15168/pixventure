from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Admin interface for the UserProfile model.
    """
    list_display = ('id', 'user')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('user',)