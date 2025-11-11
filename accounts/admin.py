"""
Admin configuration for User and UserProfile models.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, UserProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom admin for User model."""
    
    list_display = [
        'email', 'get_full_name', 'role', 'is_active', 
        'is_staff', 'date_joined'
    ]
    list_filter = ['role', 'is_active', 'is_staff', 'date_joined']
    search_fields = ['email', 'first_name', 'last_name', 'phone_number']
    ordering = ['-date_joined']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {
            'fields': ('first_name', 'last_name', 'phone_number')
        }),
        (_('Role & Permissions'), {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        (_('Important dates'), {
            'fields': ('last_login', 'date_joined')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'first_name', 'last_name', 
                'role', 'password1', 'password2'
            ),
        }),
    )
    
    readonly_fields = ['date_joined', 'last_login']
    
    def get_full_name(self, obj):
        """Display full name in list view."""
        return obj.get_full_name()
    get_full_name.short_description = 'Full Name'
    
    def save_model(self, request, obj, form, change):
        """Create profile when creating user from admin."""
        super().save_model(request, obj, form, change)
        # Ensure profile exists
        UserProfile.objects.get_or_create(user=obj)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin for UserProfile model."""
    
    list_display = [
        'user', 'date_of_birth', 'emergency_contact_name',
        'created_at', 'updated_at'
    ]
    search_fields = [
        'user__email', 'user__first_name', 'user__last_name',
        'emergency_contact_name'
    ]
    list_filter = ['created_at', 'updated_at']
    
    fieldsets = (
        (_('User'), {
            'fields': ('user',)
        }),
        (_('Personal Information'), {
            'fields': ('avatar', 'date_of_birth', 'address')
        }),
        (_('Emergency Contact'), {
            'fields': (
                'emergency_contact_name',
                'emergency_contact_number',
                'emergency_contact_relationship'
            )
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']