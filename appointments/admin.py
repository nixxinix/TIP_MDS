"""
Admin configuration for appointments models.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Appointment, AppointmentNote


class AppointmentNoteInline(admin.TabularInline):
    """Inline admin for appointment notes."""
    model = AppointmentNote
    extra = 1
    fields = ['author', 'note', 'is_internal', 'created_at']
    readonly_fields = ['created_at']


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    """Admin for Appointment model."""
    
    list_display = [
        'ticket_number', 'get_student_id', 'get_student_name',
        'service_type', 'preferred_date', 'preferred_time_slot',
        'status_badge', 'doctor', 'created_at'
    ]
    list_filter = [
        'status', 'service_type', 'preferred_time_slot',
        'preferred_date', 'created_at'
    ]
    search_fields = [
        'ticket_number', 'student__student_id',
        'student__user__first_name', 'student__user__last_name',
        'reason'
    ]
    readonly_fields = [
        'id', 'ticket_number', 'created_at', 'updated_at',
        'approved_at', 'completed_at', 'cancelled_at'
    ]
    date_hierarchy = 'preferred_date'
    inlines = [AppointmentNoteInline]
    
    fieldsets = (
        ('Appointment Information', {
            'fields': (
                'id', 'ticket_number', 'student', 'service_type'
            )
        }),
        ('Schedule', {
            'fields': (
                'preferred_date', 'preferred_time_slot', 'actual_datetime'
            )
        }),
        ('Details', {
            'fields': (
                'reason', 'doctor_notes'
            )
        }),
        ('Emergency Contact', {
            'fields': (
                'emergency_contact_name', 'emergency_contact_number'
            )
        }),
        ('Assignment', {
            'fields': (
                'doctor', 'status'
            )
        }),
        ('Approval & Completion', {
            'fields': (
                'approved_by', 'approved_at',
                'completed_at', 'cancelled_at', 'cancellation_reason'
            )
        }),
        ('Notifications', {
            'fields': ('reminder_sent',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def get_student_id(self, obj):
        """Display student ID."""
        return obj.student.student_id
    get_student_id.short_description = 'Student ID'
    get_student_id.admin_order_field = 'student__student_id'
    
    def get_student_name(self, obj):
        """Display student name."""
        return obj.student.user.get_full_name()
    get_student_name.short_description = 'Student Name'
    
    def status_badge(self, obj):
        """Display colored status badge."""
        colors = {
            'pending': '#ffc107',
            'approved': '#28a745',
            'completed': '#17a2b8',
            'cancelled': '#6c757d',
            'no_show': '#dc3545',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    actions = ['approve_appointments', 'complete_appointments', 'cancel_appointments']
    
    def approve_appointments(self, request, queryset):
        """Bulk approve selected appointments."""
        count = 0
        for appointment in queryset.filter(status='pending'):
            appointment.approve(request.user)
            count += 1
        
        self.message_user(request, f'{count} appointment(s) approved successfully.')
    approve_appointments.short_description = 'Approve selected appointments'
    
    def complete_appointments(self, request, queryset):
        """Bulk complete selected appointments."""
        count = 0
        for appointment in queryset.filter(status='approved'):
            appointment.complete()
            count += 1
        
        self.message_user(request, f'{count} appointment(s) marked as completed.')
    complete_appointments.short_description = 'Mark as completed'
    
    def cancel_appointments(self, request, queryset):
        """Bulk cancel selected appointments."""
        count = 0
        for appointment in queryset.filter(status__in=['pending', 'approved']):
            appointment.cancel(reason='Cancelled by admin')
            count += 1
        
        self.message_user(request, f'{count} appointment(s) cancelled.')
    cancel_appointments.short_description = 'Cancel selected appointments'


@admin.register(AppointmentNote)
class AppointmentNoteAdmin(admin.ModelAdmin):
    """Admin for AppointmentNote model."""
    
    list_display = [
        'appointment', 'author', 'note_preview', 'is_internal', 'created_at'
    ]
    list_filter = ['is_internal', 'created_at']
    search_fields = [
        'appointment__ticket_number', 'note',
        'author__first_name', 'author__last_name'
    ]
    readonly_fields = ['created_at']
    
    def note_preview(self, obj):
        """Display preview of note."""
        return obj.note[:50] + '...' if len(obj.note) > 50 else obj.note
    note_preview.short_description = 'Note'