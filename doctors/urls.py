"""
URL configuration for doctors app.
"""

from django.urls import path
from . import views

app_name = 'doctors'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.doctor_dashboard, name='dashboard'),
    
    # Student Search & Records
    path('search/', views.search_student, name='search'),
    path('records/create/<str:student_id>/', views.create_medical_record, name='create_record'),
    
    # Pending Requests
    path('pending/', views.pending_requests, name='pending'),
    path('requests/<uuid:request_id>/approve/', views.approve_update_request, name='approve_request'),
    path('requests/<uuid:request_id>/decline/', views.decline_update_request, name='decline_request'),
    
    # Appointments Management
    path('appointments/', views.manage_appointments, name='appointments'),
    path('appointments/<uuid:appointment_id>/', views.appointment_detail, name='appointment_detail'),
    path('appointments/<uuid:appointment_id>/approve/', views.approve_appointment, name='approve_appointment'),
    path('appointments/<uuid:appointment_id>/complete/', views.complete_appointment, name='complete_appointment'),
    path('appointments/<uuid:appointment_id>/cancel/', views.cancel_appointment, name='cancel_appointment'),
    
    # Templates & Certificates - NEW ROUTES
    path('templates/', views.templates_management, name='templates'),
    path('templates/prescription/', views.generate_prescription, name='generate_prescription'),
    path('templates/clearance/', views.generate_clearance, name='generate_clearance'),
    path('templates/certificate/', views.generate_certificate, name='generate_certificate'),
    path('templates/dental-certificate/', views.generate_dental_certificate, name='generate_dental_certificate'),
    
    # Student Lookup API for AJAX
    path('api/student-lookup/', views.student_lookup_api, name='student_lookup_api'),
    
    # Analytics & Reports
    path('analytics/', views.analytics_dashboard, name='analytics'),
    path('reports/export/', views.export_report, name='export_report'),
    
    # Settings
    path('settings/', views.settings_view, name='settings'),
]