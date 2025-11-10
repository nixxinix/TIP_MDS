"""
Main URL configuration for TIP MDS EMR project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Authentication
    path('accounts/', include('accounts.urls')),
    
    # Student Portal
    path('student/', include('students.urls')),
    
    # Doctor/Admin Portal
    path('doctor/', include('doctors.urls')),
    
    # Appointments
    path('appointments/', include('appointments.urls')),
    
    # Templates & Documents
    path('documents/', include('templates_docs.urls')),
    
    # Analytics
    path('analytics/', include('analytics.urls')),
    
    # Notifications
    path('notifications/', include('notifications.urls')),
    
    # Root redirect to login
    path('', RedirectView.as_view(url='/accounts/login/', permanent=False), name='home'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Admin site customization
admin.site.site_header = "TIP MDS EMR Administration"
admin.site.site_title = "TIP MDS EMR Admin"
admin.site.index_title = "Welcome to TIP MDS EMR Admin Portal"