"""
Notification service functions for creating and sending notifications.
"""

from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import Notification, EmailLog, NotificationPreference


def create_notification(
    recipient,
    notification_type,
    title,
    message,
    priority='normal',
    action_url=None,
    action_label=None,
    send_email=False,
    related_object_type=None,
    related_object_id=None,
    expires_in_days=30
):
    """
    Create a new notification.
    
    Args:
        recipient: User instance
        notification_type: Type of notification
        title: Notification title
        message: Notification message
        priority: Notification priority
        action_url: Optional URL for action button
        action_label: Optional label for action button
        send_email: Whether to send email
        related_object_type: Type of related object
        related_object_id: ID of related object
        expires_in_days: Days until notification expires
    
    Returns:
        Notification instance
    """
    # Check user preferences
    prefs, created = NotificationPreference.objects.get_or_create(user=recipient)
    
    # Determine if should send email based on preferences
    if send_email:
        if notification_type == 'appointment_approved':
            send_email = prefs.email_appointment_approved
        elif notification_type == 'appointment_reminder':
            send_email = prefs.email_appointment_reminder
        elif notification_type in ['request_approved', 'request_declined']:
            send_email = prefs.email_request_status
        elif notification_type == 'certificate_issued':
            send_email = prefs.email_certificate_issued
        elif notification_type == 'system':
            send_email = prefs.email_system_notifications
    
    # Create notification
    notification = Notification.objects.create(
        recipient=recipient,
        notification_type=notification_type,
        title=title,
        message=message,
        priority=priority,
        action_url=action_url,
        action_label=action_label,
        send_email=send_email,
        related_object_type=related_object_type,
        related_object_id=str(related_object_id) if related_object_id else None,
        expires_at=timezone.now() + timedelta(days=expires_in_days)
    )
    
    # Send email if requested
    if send_email:
        send_notification_email(notification)
    
    return notification


def send_notification_email(notification):
    """
    Send email for a notification.
    
    Args:
        notification: Notification instance
    
    Returns:
        Boolean indicating success
    """
    try:
        # Prepare email content
        subject = notification.title
        
        # Render email template
        context = {
            'notification': notification,
            'recipient_name': notification.recipient.get_full_name(),
            'action_url': notification.action_url,
            'action_label': notification.action_label or 'View Details',
        }
        
        html_message = render_to_string('emails/notification.html', context)
        plain_message = notification.message
        
        # Create email log
        email_log = EmailLog.objects.create(
            notification=notification,
            recipient_email=notification.recipient.email,
            recipient_name=notification.recipient.get_full_name(),
            subject=subject,
            body=plain_message
        )
        
        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[notification.recipient.email],
            html_message=html_message,
            fail_silently=False
        )
        
        # Update notification
        notification.email_sent = True
        notification.email_sent_at = timezone.now()
        notification.save(update_fields=['email_sent', 'email_sent_at'])
        
        # Update email log
        email_log.status = 'sent'
        email_log.sent_at = timezone.now()
        email_log.save(update_fields=['status', 'sent_at'])
        
        return True
        
    except Exception as e:
        # Log error
        if 'email_log' in locals():
            email_log.status = 'failed'
            email_log.error_message = str(e)
            email_log.retry_count += 1
            email_log.save()
        
        return False


def notify_appointment_approved(appointment):
    """
    Notify student that appointment was approved.
    
    Args:
        appointment: Appointment instance
    """
    message = (
        f"Your appointment request for {appointment.get_service_type_display()} "
        f"on {appointment.preferred_date.strftime('%B %d, %Y')} has been approved.\n\n"
        f"Ticket Number: {appointment.ticket_number}\n"
    )
    
    if appointment.doctor:
        message += f"Assigned Doctor: Dr. {appointment.doctor.get_full_name()}\n"
    
    if appointment.actual_datetime:
        message += f"Scheduled Time: {appointment.actual_datetime.strftime('%B %d, %Y at %I:%M %p')}\n"
    
    message += "\nPlease arrive 10 minutes before your scheduled time."
    
    create_notification(
        recipient=appointment.student.user,
        notification_type='appointment_approved',
        title='Appointment Approved',
        message=message,
        priority='high',
        action_url=f'/student/appointments/{appointment.id}/',
        action_label='View Appointment',
        send_email=True,
        related_object_type='Appointment',
        related_object_id=appointment.id
    )


def notify_appointment_reminder(appointment):
    """
    Send appointment reminder notification.
    
    Args:
        appointment: Appointment instance
    """
    message = (
        f"Reminder: You have an appointment tomorrow.\n\n"
        f"Service: {appointment.get_service_type_display()}\n"
        f"Date: {appointment.preferred_date.strftime('%B %d, %Y')}\n"
        f"Time: {appointment.get_preferred_time_slot_display()}\n"
        f"Ticket: {appointment.ticket_number}\n\n"
        f"Please arrive 10 minutes before your scheduled time."
    )
    
    create_notification(
        recipient=appointment.student.user,
        notification_type='appointment_reminder',
        title='Appointment Reminder',
        message=message,
        priority='high',
        action_url=f'/student/appointments/{appointment.id}/',
        action_label='View Appointment',
        send_email=True,
        related_object_type='Appointment',
        related_object_id=appointment.id,
        expires_in_days=2
    )


def notify_request_approved(update_request):
    """
    Notify student that update request was approved.
    
    Args:
        update_request: RecordUpdateRequest instance
    """
    message = (
        f"Your request to update {update_request.field_name.replace('_', ' ').title()} "
        f"has been approved.\n\n"
        f"The changes have been applied to your profile."
    )
    
    create_notification(
        recipient=update_request.student.user,
        notification_type='request_approved',
        title='Update Request Approved',
        message=message,
        priority='normal',
        action_url='/student/profile/',
        action_label='View Profile',
        send_email=True,
        related_object_type='RecordUpdateRequest',
        related_object_id=update_request.id
    )


def notify_request_declined(update_request):
    """
    Notify student that update request was declined.
    
    Args:
        update_request: RecordUpdateRequest instance
    """
    message = (
        f"Your request to update {update_request.field_name.replace('_', ' ').title()} "
        f"has been declined.\n\n"
    )
    
    if update_request.review_notes:
        message += f"Reason: {update_request.review_notes}\n\n"
    
    message += "Please contact the medical office if you have questions."
    
    create_notification(
        recipient=update_request.student.user,
        notification_type='request_declined',
        title='Update Request Declined',
        message=message,
        priority='normal',
        send_email=True,
        related_object_type='RecordUpdateRequest',
        related_object_id=update_request.id
    )


def notify_certificate_issued(certificate):
    """
    Notify student that certificate was issued.
    
    Args:
        certificate: IssuedCertificate instance
    """
    message = (
        f"A new certificate has been issued for you.\n\n"
        f"Certificate: {certificate.title}\n"
        f"Certificate Number: {certificate.certificate_number}\n"
        f"Date Issued: {certificate.date_issued.strftime('%B %d, %Y')}\n"
    )
    
    if certificate.valid_until:
        message += f"Valid Until: {certificate.valid_until.strftime('%B %d, %Y')}\n"
    
    message += "\nYou can download your certificate from your dashboard."
    
    create_notification(
        recipient=certificate.student.user,
        notification_type='certificate_issued',
        title='Certificate Issued',
        message=message,
        priority='high',
        action_url=f'/student/certificates/{certificate.id}/',
        action_label='Download Certificate',
        send_email=True,
        related_object_type='IssuedCertificate',
        related_object_id=certificate.id
    )


def send_appointment_reminders():
    """
    Send reminders for upcoming appointments.
    Should be run as a scheduled task (daily).
    
    Returns:
        Number of reminders sent
    """
    from appointments.models import Appointment
    
    tomorrow = timezone.now().date() + timedelta(days=1)
    
    # Get approved appointments for tomorrow that haven't been reminded
    appointments = Appointment.objects.filter(
        status='approved',
        preferred_date=tomorrow,
        reminder_sent=False
    ).select_related('student__user')
    
    count = 0
    for appointment in appointments:
        # Check user preferences
        prefs = NotificationPreference.objects.filter(user=appointment.student.user).first()
        if prefs and prefs.email_appointment_reminder:
            notify_appointment_reminder(appointment)
            appointment.reminder_sent = True
            appointment.save(update_fields=['reminder_sent'])
            count += 1
    
    return count


def mark_expired_notifications():
    """
    Mark expired notifications as read.
    Should be run as a scheduled task.
    
    Returns:
        Number of notifications marked as read
    """
    expired = Notification.objects.filter(
        expires_at__lt=timezone.now(),
        is_read=False
    )
    
    count = expired.count()
    expired.update(is_read=True, read_at=timezone.now())
    
    return count

def notify_appointment_cancelled(appointment):
    """Notify student when appointment is cancelled by doctor."""
    from .models import Notification
    from django.core.mail import send_mail
    from django.conf import settings
    
    message = (
        f'Your appointment (Ticket: {appointment.ticket_number}) scheduled for '
        f'{appointment.preferred_date.strftime("%B %d, %Y")} has been cancelled.\n\n'
        f'Reason: {appointment.cancellation_reason}\n\n'
        f'You can book a new appointment through your student portal.'
    )
    
    # Create in-app notification
    Notification.objects.create(
        user=appointment.student.user,
        title='Appointment Cancelled',
        message=message,
        notification_type='appointment',
        related_appointment=appointment
    )
    
    # Send email notification
    try:
        send_mail(
            subject=f'Appointment Cancelled - {appointment.ticket_number}',
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[appointment.student.user.email],
            fail_silently=True,
        )
    except Exception as e:
        print(f"Failed to send cancellation email: {e}")