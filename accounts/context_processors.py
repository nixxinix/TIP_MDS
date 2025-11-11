"""
Context processors to make variables available in all templates.
"""

from notifications.models import Notification


def notifications_processor(request):
    """
    Add unread notification count to all templates.
    """
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()
        
        recent_notifications = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).order_by('-created_at')[:5]
        
        return {
            'unread_notifications_count': unread_count,
            'recent_notifications': recent_notifications,
        }
    
    return {
        'unread_notifications_count': 0,
        'recent_notifications': [],
    }


def user_role_processor(request):
    """
    Add user role information to all templates.
    """
    if request.user.is_authenticated:
        return {
            'is_student': request.user.is_student(),
            'is_doctor': request.user.is_doctor(),
            'is_admin': request.user.is_admin_user(),
            'user_role': request.user.role,
        }
    
    return {
        'is_student': False,
        'is_doctor': False,
        'is_admin': False,
        'user_role': None,
    }