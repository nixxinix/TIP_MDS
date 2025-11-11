"""
Admin configuration for doctor models.
"""

from django.contrib import admin
from .models import DoctorProfile


@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    """Admin for DoctorProfile model."""
    
    list_display = [
        'get_full_title', 'license_number', 'specialization',
        'department', 'is_active', 'is_available_for_appointments'
    ]
    list_filter = [
        'specialization', 'department', 'is_active',
        'is_available_for_appointments'
    ]
    search_fields = [
        'user__first_name', 'user__last_name', 'user__email',
        'license_number', 'department'
    ]
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User Account', {
            'fields': ('user',)
        }),
        ('Professional Information', {
            'fields': (
                'license_number', 'specialization', 'department',
                'years_of_experience', 'qualifications'
            )
        }),
        ('Contact & Schedule', {
            'fields': (
                'office_location', 'consultation_hours'
            )
        }),
        ('Digital Signature', {
            'fields': ('signature_image',)
        }),
        ('Status', {
            'fields': ('is_active', 'is_available_for_appointments')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def get_full_title(self, obj):
        """Display doctor's name with title."""
        return obj.get_full_title()
    get_full_title.short_description = 'Doctor Name'