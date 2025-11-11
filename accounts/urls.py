"""
URL configuration for accounts app.
"""

from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('login/', views.login_view, name='login'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Profile Management
    path('profile/', views.profile_view, name='profile'),
    path('profile/change-password/', views.change_password_view, name='change_password'),
    
    # Admin - User Management (NEW)
    path('users/', views.user_management_view, name='user_management'),
    path('users/add/', views.add_user_view, name='add_user'),
    path('users/<int:user_id>/', views.view_user_detail, name='view_user'),
    path('users/<int:user_id>/deactivate/', views.deactivate_user, name='deactivate_user'),
    path('users/<int:user_id>/reset-password/', views.reset_user_password, name='reset_password'),
    
    # API Endpoints
    path('api/check-email/', views.check_email_api, name='check_email_api'),
]