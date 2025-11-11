"""
Views for notifications.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from .models import Notification, NotificationPreference


@login_required
def notification_list(request):
    """List all notifications for current user."""
    
    notifications = Notification.objects.filter(
        recipient=request.user
    ).order_by('-created_at')
    
    # Separate unread and read
    unread_notifications = notifications.filter(is_read=False)
    read_notifications = notifications.filter(is_read=True)[:20]  # Limit read to 20
    
    context = {
        'unread_notifications': unread_notifications,
        'read_notifications': read_notifications,
    }
    
    return render(request, 'notifications/notification-list.html', context)


@login_required
def mark_notification_read(request, notification_id):
    """Mark a notification as read."""
    
    notification = get_object_or_404(
        Notification,
        id=notification_id,
        recipient=request.user
    )
    
    notification.mark_as_read()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    return redirect('notifications:list')


@login_required
def mark_all_read(request):
    """Mark all notifications as read."""
    
    Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).update(is_read=True)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    return redirect('notifications:list')


@login_required
def notification_count(request):
    """Get unread notification count (API endpoint)."""
    
    count = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).count()
    
    return JsonResponse({'count': count})


@login_required
def notification_preferences(request):
    """Manage notification preferences."""
    
    preferences, created = NotificationPreference.objects.get_or_create(
        user=request.user
    )
    
    if request.method == 'POST':
        # Update preferences
        preferences.email_appointment_approved = request.POST.get('email_appointment_approved') == 'on'
        preferences.email_appointment_reminder = request.POST.get('email_appointment_reminder') == 'on'
        preferences.email_request_status = request.POST.get('email_request_status') == 'on'
        preferences.email_certificate_issued = request.POST.get('email_certificate_issued') == 'on'
        preferences.email_system_notifications = request.POST.get('email_system_notifications') == 'on'
        
        preferences.inapp_appointment_updates = request.POST.get('inapp_appointment_updates') == 'on'
        preferences.inapp_request_updates = request.POST.get('inapp_request_updates') == 'on'
        preferences.inapp_system_notifications = request.POST.get('inapp_system_notifications') == 'on'
        
        reminder_hours = request.POST.get('appointment_reminder_hours')
        if reminder_hours:
            preferences.appointment_reminder_hours = int(reminder_hours)
        
        preferences.save()
        
        from django.contrib import messages
        messages.success(request, 'Notification preferences updated successfully.')
        return redirect('notifications:preferences')
    
    context = {
        'preferences': preferences
    }
    
    return render(request, 'notifications/preferences.html', context)