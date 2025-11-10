"""
Notifications models for TIP MDS EMR system.
Handles in-app and email notifications.
"""

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import uuid


class Notification(models.Model):
    """
    In-app notifications for users.
    Tracks messages, status, and delivery.
    """
    
    NOTIFICATION_TYPE_CHOICES = (
        ('appointment_approved', 'Appointment Approved'),
        ('appointment_reminder', 'Appointment Reminder'),
        ('appointment_cancelled', 'Appointment Cancelled'),
        ('request_approved', 'Update Request Approved'),
        ('request_declined', 'Update Request Declined'),
        ('request_expiring', 'Request Expiring Soon'),
        ('certificate_issued', 'Certificate Issued'),
        ('prescription_issued', 'Prescription Issued'),
        ('system', 'System Notification'),
        ('other', 'Other'),
    )
    
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    )
    
    # Unique identifier
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    # Recipient
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    
    # Notification Details
    notification_type = models.CharField(
        max_length=30,
        choices=NOTIFICATION_TYPE_CHOICES,
        default='system'
    )
    
    title = models.CharField(
        max_length=200,
        help_text=_('Notification title')
    )
    
    message = models.TextField(
        help_text=_('Notification message content')
    )
    
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='normal'
    )
    
    # Action Link (optional)
    action_url = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        help_text=_('URL for action button')
    )
    
    action_label = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text=_('Label for action button')
    )
    
    # Related Objects (optional)
    related_object_type = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text=_('Type of related object (e.g., Appointment, Certificate)')
    )
    
    related_object_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text=_('ID of related object')
    )
    
    # Status
    is_read = models.BooleanField(
        default=False,
        help_text=_('Whether notification has been read')
    )
    
    read_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text=_('When notification was read')
    )
    
    # Email Delivery
    send_email = models.BooleanField(
        default=False,
        help_text=_('Whether to send email notification')
    )
    
    email_sent = models.BooleanField(
        default=False,
        help_text=_('Whether email was sent')
    )
    
    email_sent_at = models.DateTimeField(
        blank=True,
        null=True
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text=_('When notification expires and can be auto-deleted')
    )
    
    class Meta:
        verbose_name = _('notification')
        verbose_name_plural = _('notifications')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['notification_type']),
            models.Index(fields=['created_at']),
            models.Index(fields=['priority']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.recipient.email}"
    
    def mark_as_read(self):
        """Mark notification as read."""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])
    
    def mark_as_unread(self):
        """Mark notification as unread."""
        self.is_read = False
        self.read_at = None
        self.save(update_fields=['is_read', 'read_at'])
    
    def is_expired(self):
        """Check if notification has expired."""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False


class EmailLog(models.Model):
    """
    Log of all emails sent by the system.
    Tracks delivery status and errors.
    """
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('bounced', 'Bounced'),
    )
    
    # Unique identifier
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    # Related notification (optional)
    notification = models.ForeignKey(
        Notification,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='email_logs'
    )
    
    # Email Details
    recipient_email = models.EmailField(
        help_text=_('Email recipient address')
    )
    
    recipient_name = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )
    
    subject = models.CharField(
        max_length=200,
        help_text=_('Email subject line')
    )
    
    body = models.TextField(
        help_text=_('Email body content')
    )
    
    # Status
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    error_message = models.TextField(
        blank=True,
        null=True,
        help_text=_('Error message if sending failed')
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(
        blank=True,
        null=True
    )
    
    # Retry tracking
    retry_count = models.PositiveIntegerField(
        default=0,
        help_text=_('Number of send attempts')
    )
    
    max_retries = models.PositiveIntegerField(
        default=3,
        help_text=_('Maximum number of retry attempts')
    )
    
    class Meta:
        verbose_name = _('email log')
        verbose_name_plural = _('email logs')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient_email']),
            models.Index(fields=['status', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.subject} to {self.recipient_email} ({self.status})"
    
    def can_retry(self):
        """Check if email can be retried."""
        return self.status == 'failed' and self.retry_count < self.max_retries


class NotificationPreference(models.Model):
    """
    User notification preferences.
    Controls which notifications to receive.
    """
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_preferences',
        primary_key=True
    )
    
    # Email Notifications
    email_appointment_approved = models.BooleanField(
        default=True,
        help_text=_('Receive email when appointment is approved')
    )
    
    email_appointment_reminder = models.BooleanField(
        default=True,
        help_text=_('Receive appointment reminder emails')
    )
    
    email_request_status = models.BooleanField(
        default=True,
        help_text=_('Receive email when update request status changes')
    )
    
    email_certificate_issued = models.BooleanField(
        default=True,
        help_text=_('Receive email when certificate is issued')
    )
    
    email_system_notifications = models.BooleanField(
        default=True,
        help_text=_('Receive system notification emails')
    )
    
    # In-App Notifications
    inapp_appointment_updates = models.BooleanField(
        default=True,
        help_text=_('Show in-app notifications for appointments')
    )
    
    inapp_request_updates = models.BooleanField(
        default=True,
        help_text=_('Show in-app notifications for requests')
    )
    
    inapp_system_notifications = models.BooleanField(
        default=True,
        help_text=_('Show system notifications in-app')
    )
    
    # Reminder Settings
    appointment_reminder_hours = models.PositiveIntegerField(
        default=24,
        help_text=_('Hours before appointment to send reminder')
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('notification preference')
        verbose_name_plural = _('notification preferences')
    
    def __str__(self):
        return f"Notification Preferences - {self.user.email}"