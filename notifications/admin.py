"""
Admin configuration for notifications models.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Notification, EmailLog, NotificationPreference


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin for Notification model."""
    
    list_display = [
        'title', 'recipient', 'notification_type',
        'priority_badge', 'is_read', 'email_sent',
        'created_at'
    ]
    list_filter = [
        'notification_type', 'priority', 'is_read',
        'email_sent', 'created_at'
    ]
    search_fields = [
        'title', 'message', 'recipient__email',
        'recipient__first_name', 'recipient__last_name'
    ]
    readonly_fields = ['id', 'created_at', 'read_at', 'email_sent_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Notification Information', {
            'fields': ('id', 'recipient', 'notification_type', 'priority')
        }),
        ('Content', {
            'fields': ('title', 'message')
        }),
        ('Action', {
            'fields': ('action_url', 'action_label')
        }),
        ('Related Object', {
            'fields': ('related_object_type', 'related_object_id')
        }),
        ('Status', {
            'fields': ('is_read', 'read_at', 'expires_at')
        }),
        ('Email', {
            'fields': ('send_email', 'email_sent', 'email_sent_at')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )
    
    def priority_badge(self, obj):
        """Display colored priority badge."""
        colors = {
            'low': '#6c757d',
            'normal': '#17a2b8',
            'high': '#ffc107',
            'urgent': '#dc3545',
        }
        color = colors.get(obj.priority, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_priority_display()
        )
    priority_badge.short_description = 'Priority'
    
    actions = ['mark_as_read', 'mark_as_unread']
    
    def mark_as_read(self, request, queryset):
        """Mark selected notifications as read."""
        count = 0
        for notif in queryset:
            notif.mark_as_read()
            count += 1
        self.message_user(request, f'{count} notification(s) marked as read.')
    mark_as_read.short_description = 'Mark as read'
    
    def mark_as_unread(self, request, queryset):
        """Mark selected notifications as unread."""
        count = 0
        for notif in queryset:
            notif.mark_as_unread()
            count += 1
        self.message_user(request, f'{count} notification(s) marked as unread.')
    mark_as_unread.short_description = 'Mark as unread'


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    """Admin for EmailLog model."""
    
    list_display = [
        'subject', 'recipient_email', 'status_badge',
        'retry_count', 'created_at', 'sent_at'
    ]
    list_filter = ['status', 'created_at', 'sent_at']
    search_fields = ['recipient_email', 'subject', 'body']
    readonly_fields = ['id', 'created_at', 'sent_at', 'retry_count']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Email Information', {
            'fields': ('id', 'notification', 'recipient_email', 'recipient_name')
        }),
        ('Content', {
            'fields': ('subject', 'body')
        }),
        ('Status', {
            'fields': ('status', 'error_message')
        }),
        ('Retry', {
            'fields': ('retry_count', 'max_retries')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'sent_at')
        }),
    )
    
    def status_badge(self, obj):
        """Display colored status badge."""
        colors = {
            'pending': '#ffc107',
            'sent': '#28a745',
            'failed': '#dc3545',
            'bounced': '#6c757d',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    actions = ['retry_failed_emails']
    
    def retry_failed_emails(self, request, queryset):
        """Retry sending failed emails."""
        from .services import send_notification_email
        
        count = 0
        for email_log in queryset:
            if email_log.can_retry() and email_log.notification:
                if send_notification_email(email_log.notification):
                    count += 1
        
        self.message_user(request, f'{count} email(s) retried successfully.')
    retry_failed_emails.short_description = 'Retry failed emails'


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    """Admin for NotificationPreference model."""
    
    list_display = [
        'user', 'email_appointment_approved', 'email_appointment_reminder',
        'email_request_status', 'email_certificate_issued',
        'updated_at'
    ]
    list_filter = [
        'email_appointment_approved', 'email_appointment_reminder',
        'email_request_status', 'updated_at'
    ]
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Email Notifications', {
            'fields': (
                'email_appointment_approved', 'email_appointment_reminder',
                'email_request_status', 'email_certificate_issued',
                'email_system_notifications'
            )
        }),
        ('In-App Notifications', {
            'fields': (
                'inapp_appointment_updates', 'inapp_request_updates',
                'inapp_system_notifications'
            )
        }),
        ('Reminder Settings', {
            'fields': ('appointment_reminder_hours',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )