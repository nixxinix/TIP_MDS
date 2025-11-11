"""
URL configuration for notifications app.
"""

from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    # Notification Management
    path('', views.notification_list, name='list'),
    path('<uuid:notification_id>/read/', views.mark_notification_read, name='mark_read'),
    path('mark-all-read/', views.mark_all_read, name='mark_all_read'),
    
    # API Endpoints
    path('api/count/', views.notification_count, name='count_api'),
    
    # Preferences
    path('preferences/', views.notification_preferences, name='preferences'),
]