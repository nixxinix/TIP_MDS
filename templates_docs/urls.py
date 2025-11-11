"""
URL configuration for templates_docs app.
"""

from django.urls import path
from django.views.generic import TemplateView

app_name = 'templates_docs'

# Templates and documents are primarily managed through doctor portal
# Certificate downloads are handled through student portal

urlpatterns = [
    # Placeholder for potential public certificate verification
    # path('verify/<str:certificate_number>/', views.verify_certificate, name='verify_certificate'),
]