"""
URL configuration for students app.
"""

from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.student_dashboard, name='dashboard'),
    
    # Registration
    path('register/', views.student_registration, name='register'),
    
    # Profile Update
    path('update/', views.student_update, name='update'),
    
    # Medical Records
    path('records/', views.student_records, name='records'),
    path('records/<uuid:record_id>/', views.record_detail, name='record_detail'),
    path('records/request-update/', views.request_update, name='request_update'),
    
    # Appointments
    path('appointments/', views.student_appointments, name='appointments'),
    path('appointments/<uuid:appointment_id>/', views.appointment_detail, name='appointment_detail'),
    path('appointments/<uuid:appointment_id>/cancel/', views.cancel_appointment, name='cancel_appointment'),
    
    # Certificates
    path('certificates/', views.student_certificates, name='certificates'),
]