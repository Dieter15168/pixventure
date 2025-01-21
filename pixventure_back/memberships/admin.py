from django.contrib import admin
from .models import MembershipPlan, UserMembership

@admin.register(MembershipPlan)
class MembershipPlanAdmin(admin.ModelAdmin):
    """
    Admin interface for the MembershipPlan model.
    """
    list_display = ('id', 'name', 'duration_days', 'price', 'currency', 'is_active')
    list_filter = ('is_active', 'currency')
    search_fields = ('name',)
    ordering = ('-id',)
    fieldsets = (
        (None, {
            'fields': ('name', 'duration_days', 'price', 'currency', 'is_active'),
        }),
    )


@admin.register(UserMembership)
class UserMembershipAdmin(admin.ModelAdmin):
    """
    Admin interface for the UserMembership model.
    """
    list_display = ('id', 'user', 'plan', 'start_date', 'end_date', 'is_active', 'is_currently_active')
    list_filter = ('is_active', 'plan', 'start_date', 'end_date')
    search_fields = ('user__username', 'plan__name')
    readonly_fields = ('start_date', 'is_currently_active')
    ordering = ('-start_date',)
    fieldsets = (
        (None, {
            'fields': ('user', 'plan', 'start_date', 'end_date', 'is_active'),
        }),
        ('Status', {
            'fields': ('is_currently_active',),
        }),
    )

    def is_currently_active(self, obj):
        """
        Display whether the membership is currently active based on the calculated property.
        """
        return obj.is_currently_active
    is_currently_active.boolean = True  # Display as a boolean indicator
    is_currently_active.short_description = "Currently Active"