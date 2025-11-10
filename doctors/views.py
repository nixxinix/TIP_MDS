"""
Views for doctor/admin portal.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from accounts.decorators import doctor_required
from students.models import StudentProfile, MedicalRecord, RecordUpdateRequest
from students.forms import MedicalRecordForm
from appointments.models import Appointment
from appointments.forms import AppointmentApprovalForm, AppointmentSearchForm
from templates_docs.models import IssuedCertificate, Prescription, Template
from templates_docs.forms import CertificateGenerationForm, PrescriptionForm
from templates_docs.utils import generate_certificate_pdf, generate_prescription_pdf
from analytics.services import (
    get_top_morbidities,
    get_consultation_statistics,
    get_daily_consultation_trend,
    get_service_distribution
)
from analytics.exports import (
    export_morbidity_report_csv,
    export_morbidity_report_pdf,
    export_consultation_report_csv,
    export_consultation_report_pdf
)
from notifications.services import (
    notify_appointment_approved,
    notify_request_approved,
    notify_request_declined,
    notify_certificate_issued
)


@login_required
@doctor_required
def doctor_dashboard(request):
    """Doctor/Admin dashboard view."""
    
    # Statistics
    total_patients = StudentProfile.objects.filter(is_verified=True).count()
    
    today_appointments = Appointment.objects.filter(
        preferred_date=timezone.now().date(),
        status__in=['approved', 'pending']
    ).count()
    
    pending_requests = RecordUpdateRequest.objects.filter(
        status='pending'
    ).count()
    
    active_cases = MedicalRecord.objects.filter(
        status='approved',
        visit_date__gte=timezone.now().date() - timezone.timedelta(days=30)
    ).count()
    
    # Recent activity
    recent_appointments = Appointment.objects.select_related(
        'student__user', 'doctor'
    ).order_by('-created_at')[:10]
    
    pending_update_requests = RecordUpdateRequest.objects.select_related(
        'student__user'
    ).filter(status='pending').order_by('-created_at')[:5]
    
    context = {
        'total_patients': total_patients,
        'today_appointments': today_appointments,
        'pending_requests': pending_requests,
        'active_cases': active_cases,
        'recent_appointments': recent_appointments,
        'pending_update_requests': pending_update_requests,
    }
    
    return render(request, 'doctor/doctor-dashboard.html', context)


@login_required
@doctor_required
def search_student(request):
    """Search for student records."""
    
    student_profile = None
    medical_records = []
    dental_records = []
    appointments = []
    update_requests = []
    
    if request.method == 'GET' and 'student_id' in request.GET:
        student_id = request.GET.get('student_id')
        
        try:
            student_profile = StudentProfile.objects.select_related('user').get(
                student_id=student_id
            )
            
            # Get medical records
            medical_records = MedicalRecord.objects.filter(
                student=student_profile,
                record_type='medical'
            ).select_related('doctor').order_by('-visit_date')
            
            # Get dental records
            dental_records = MedicalRecord.objects.filter(
                student=student_profile,
                record_type='dental'
            ).select_related('doctor').order_by('-visit_date')
            
            # Get appointments
            appointments = Appointment.objects.filter(
                student=student_profile
            ).select_related('doctor').order_by('-preferred_date')
            
            # Get update requests
            update_requests = RecordUpdateRequest.objects.filter(
                student=student_profile
            ).order_by('-created_at')
            
        except StudentProfile.DoesNotExist:
            messages.error(request, f'No student found with ID: {student_id}')
    
    context = {
        'student_profile': student_profile,
        'medical_records': medical_records,
        'dental_records': dental_records,
        'appointments': appointments,
        'update_requests': update_requests,
    }
    
    return render(request, 'doctor/doctor-search.html', context)


@login_required
@doctor_required
def pending_requests(request):
    """View pending update requests and appointments."""
    
    # Pending update requests
    update_requests = RecordUpdateRequest.objects.filter(
        status='pending'
    ).select_related('student__user').order_by('-created_at')
    
    # Pending appointments
    pending_appointments = Appointment.objects.filter(
        status='pending'
    ).select_related('student__user').order_by('-created_at')
    
    context = {
        'update_requests': update_requests,
        'pending_appointments': pending_appointments,
    }
    
    return render(request, 'doctor/doctor-pending.html', context)


@login_required
@doctor_required
def approve_update_request(request, request_id):
    """Approve student update request."""
    
    update_request = get_object_or_404(RecordUpdateRequest, id=request_id)
    
    if update_request.status == 'pending':
        update_request.approve(request.user, apply_changes=True)
        
        # Send notification
        notify_request_approved(update_request)
        
        messages.success(request, 'Update request approved and applied.')
    else:
        messages.error(request, 'This request has already been processed.')
    
    return redirect('doctors:pending')


@login_required
@doctor_required
def decline_update_request(request, request_id):
    """Decline student update request."""
    
    update_request = get_object_or_404(RecordUpdateRequest, id=request_id)
    
    if request.method == 'POST':
        notes = request.POST.get('notes', '')
        
        if update_request.status == 'pending':
            update_request.decline(request.user, notes=notes)
            
            # Send notification
            notify_request_declined(update_request)
            
            messages.success(request, 'Update request declined.')
        else:
            messages.error(request, 'This request has already been processed.')
        
        return redirect('doctors:pending')
    
    context = {'update_request': update_request}
    return render(request, 'doctor/decline-request.html', context)


@login_required
@doctor_required
def manage_appointments(request):
    """Manage all appointments."""
    
    # Filter logic
    form = AppointmentSearchForm(request.GET or None)
    appointments = Appointment.objects.select_related(
        'student__user', 'doctor'
    ).order_by('-preferred_date', '-created_at')
    
    if form.is_valid():
        if form.cleaned_data.get('search_query'):
            query = form.cleaned_data['search_query']
            appointments = appointments.filter(
                Q(ticket_number__icontains=query) |
                Q(student__student_id__icontains=query) |
                Q(student__user__first_name__icontains=query) |
                Q(student__user__last_name__icontains=query)
            )
        
        if form.cleaned_data.get('service_type'):
            appointments = appointments.filter(
                service_type=form.cleaned_data['service_type']
            )
        
        if form.cleaned_data.get('status'):
            appointments = appointments.filter(
                status=form.cleaned_data['status']
            )
        
        if form.cleaned_data.get('date_from'):
            appointments = appointments.filter(
                preferred_date__gte=form.cleaned_data['date_from']
            )
        
        if form.cleaned_data.get('date_to'):
            appointments = appointments.filter(
                preferred_date__lte=form.cleaned_data['date_to']
            )
    
    context = {
        'form': form,
        'appointments': appointments,
    }
    
    return render(request, 'doctor/doctor-appointments.html', context)


@login_required
@doctor_required
def approve_appointment(request, appointment_id):
    """Approve an appointment."""
    
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    if request.method == 'POST':
        form = AppointmentApprovalForm(request.POST, instance=appointment)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.approve(
                approved_by_user=request.user,
                doctor=form.cleaned_data.get('doctor'),
                actual_datetime=form.cleaned_data.get('actual_datetime')
            )
            
            # Send notification
            notify_appointment_approved(appointment)
            
            messages.success(request, 'Appointment approved successfully.')
            return redirect('doctors:appointments')
    else:
        form = AppointmentApprovalForm(instance=appointment)
    
    context = {
        'form': form,
        'appointment': appointment
    }
    
    return render(request, 'doctor/approve-appointment.html', context)


@login_required
@doctor_required
def create_medical_record(request, student_id):
    """Create a new medical/dental record."""
    
    student_profile = get_object_or_404(StudentProfile, student_id=student_id)
    
    if request.method == 'POST':
        form = MedicalRecordForm(request.POST, request.FILES)
        if form.is_valid():
            record = form.save(commit=False)
            record.student = student_profile
            record.doctor = request.user
            record.status = 'approved'  # Doctors create approved records
            record.approved_by = request.user
            record.approved_at = timezone.now()
            record.save()
            
            messages.success(request, 'Medical record created successfully.')
            return redirect('doctors:search') + f'?student_id={student_id}'
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = MedicalRecordForm()
    
    context = {
        'form': form,
        'student_profile': student_profile
    }
    
    return render(request, 'doctor/create-record.html', context)


@login_required
@doctor_required
def generate_certificate(request):
    """Generate certificate for student."""
    
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        student_profile = get_object_or_404(StudentProfile, student_id=student_id)
        
        form = CertificateGenerationForm(request.POST)
        if form.is_valid():
            certificate = form.save(commit=False)
            certificate.student = student_profile
            certificate.doctor = request.user
            certificate.save()
            
            # Generate PDF
            pdf_file = generate_certificate_pdf(certificate)
            certificate.pdf_file.save(
                f"certificate_{certificate.certificate_number}.pdf",
                pdf_file,
                save=True
            )
            
            # Send notification
            notify_certificate_issued(certificate)
            
            messages.success(
                request,
                f'Certificate generated successfully! Certificate No: {certificate.certificate_number}'
            )
            return redirect('doctors:templates')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CertificateGenerationForm()
    
    context = {'form': form}
    return render(request, 'doctor/generate-certificate.html', context)


@login_required
@doctor_required
def templates_management(request):
    """Manage document templates."""
    
    templates = Template.objects.filter(is_active=True).order_by('template_type', 'name')
    
    recent_certificates = IssuedCertificate.objects.select_related(
        'student__user', 'doctor'
    ).order_by('-created_at')[:10]
    
    context = {
        'templates': templates,
        'recent_certificates': recent_certificates,
    }
    
    return render(request, 'doctor/doctor-templates.html', context)


@login_required
@doctor_required
def analytics_dashboard(request):
    """Analytics and reports dashboard."""
    
    # Date range
    date_to = timezone.now().date()
    date_from = date_to - timezone.timedelta(days=30)
    
    # Get statistics
    consultation_stats = get_consultation_statistics(date_from, date_to)
    
    medical_morbidities = get_top_morbidities('medical', limit=5, date_from=date_from, date_to=date_to)
    dental_morbidities = get_top_morbidities('dental', limit=5, date_from=date_from, date_to=date_to)
    
    daily_trend = get_daily_consultation_trend(days=30)
    service_distribution = get_service_distribution(date_from, date_to)
    
    context = {
        'consultation_stats': consultation_stats,
        'medical_morbidities': medical_morbidities,
        'dental_morbidities': dental_morbidities,
        'daily_trend': daily_trend,
        'service_distribution': service_distribution,
        'date_from': date_from,
        'date_to': date_to,
    }
    
    return render(request, 'doctor/doctor-analytics.html', context)


@login_required
@doctor_required
def export_report(request):
    """Export reports to CSV or PDF."""
    
    report_type = request.GET.get('type')
    format_type = request.GET.get('format', 'pdf')
    date_from = request.GET.get('date_from', timezone.now().date() - timezone.timedelta(days=30))
    date_to = request.GET.get('date_to', timezone.now().date())
    
    if report_type == 'morbidity':
        morbidities = get_top_morbidities('medical', limit=10, date_from=date_from, date_to=date_to)
        
        if format_type == 'csv':
            return export_morbidity_report_csv(morbidities, date_from, date_to)
        else:
            return export_morbidity_report_pdf(morbidities, date_from, date_to, 'medical')
    
    elif report_type == 'consultation':
        stats = get_consultation_statistics(date_from, date_to)
        
        if format_type == 'csv':
            return export_consultation_report_csv(stats, date_from, date_to)
        else:
            return export_consultation_report_pdf(stats, date_from, date_to)
    
    messages.error(request, 'Invalid report type.')
    return redirect('doctors:analytics')


@login_required
@doctor_required
def settings_view(request):
    """System settings view."""
    
    # Get doctor profile if exists
    doctor_profile = None
    if hasattr(request.user, 'doctor_profile'):
        doctor_profile = request.user.doctor_profile
    
    # User management (admins only)
    from accounts.models import User
    users = None
    if request.user.is_admin_user():
        users = User.objects.all().order_by('-date_joined')[:20]
    
    context = {
        'doctor_profile': doctor_profile,
        'users': users,
    }
    
    return render(request, 'doctor/doctor-settings.html', context)

@login_required
@doctor_required
def appointment_detail(request, appointment_id):
    """View appointment details (doctor view)."""
    
    appointment = get_object_or_404(
        Appointment.objects.select_related('student__user', 'doctor'),
        id=appointment_id
    )
    
    # Get student's medical records for context
    medical_records = MedicalRecord.objects.filter(
        student=appointment.student,
        record_type='medical'
    ).select_related('doctor').order_by('-visit_date')[:5]
    
    context = {
        'appointment': appointment,
        'medical_records': medical_records,
    }
    
    return render(request, 'doctor/appointment-detail.html', context)


@login_required
@doctor_required
def complete_appointment(request, appointment_id):
    """Mark an appointment as completed."""
    
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    if appointment.status != 'approved':
        messages.error(request, 'Only approved appointments can be marked as completed.')
        return redirect('doctors:appointments')
    
    if request.method == 'POST':
        notes = request.POST.get('notes', '')
        
        # Update appointment status
        appointment.status = 'completed'
        appointment.completed_at = timezone.now()
        appointment.notes = notes
        appointment.save()
        
        messages.success(request, 'Appointment marked as completed.')
        return redirect('doctors:appointments')
    
    context = {'appointment': appointment}
    return render(request, 'doctor/complete-appointment.html', context)

@login_required
@doctor_required
def appointment_detail(request, appointment_id):
    """View appointment details (doctor view)."""
    
    appointment = get_object_or_404(
        Appointment.objects.select_related('student__user', 'doctor'),
        id=appointment_id
    )
    
    # Get student's medical records for context
    medical_records = MedicalRecord.objects.filter(
        student=appointment.student,
        record_type='medical'
    ).select_related('doctor').order_by('-visit_date')[:5]
    
    context = {
        'appointment': appointment,
        'medical_records': medical_records,
    }
    
    return render(request, 'doctor/appointment-detail.html', context)


@login_required
@doctor_required
def complete_appointment(request, appointment_id):
    """Mark an appointment as completed."""
    
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    if appointment.status != 'approved':
        messages.error(request, 'Only approved appointments can be marked as completed.')
        return redirect('doctors:appointments')
    
    if request.method == 'POST':
        notes = request.POST.get('notes', '')
        
        # Update appointment status
        appointment.status = 'completed'
        appointment.completed_at = timezone.now()
        appointment.doctor_notes = notes
        appointment.save()
        
        messages.success(request, 'Appointment marked as completed.')
        return redirect('doctors:appointments')
    
    context = {'appointment': appointment}
    return render(request, 'doctor/complete-appointment.html', context)


@login_required
@doctor_required
def cancel_appointment(request, appointment_id):
    """Cancel an appointment."""
    
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Only allow cancellation of pending or approved appointments
    if appointment.status not in ['pending', 'approved']:
        messages.error(request, 'This appointment cannot be cancelled.')
        return redirect('doctors:appointment_detail', appointment_id=appointment_id)
    
    if request.method == 'POST':
        cancellation_reason = request.POST.get('cancellation_reason', '')
        
        # Use the model's cancel method
        appointment.cancel(reason=cancellation_reason, cancelled_by=request.user)
        
        # Send notification to student
        from notifications.services import notify_appointment_cancelled
        try:
            notify_appointment_cancelled(appointment)
        except:
            pass  # Continue even if notification fails
        
        messages.success(request, 'Appointment has been cancelled and student has been notified.')
        return redirect('doctors:appointments')
    
    context = {'appointment': appointment}
    return render(request, 'doctor/cancel-appointment.html', context)

# ============================================
# NEW TEMPLATE GENERATION VIEWS
# ============================================

@login_required
@doctor_required
def generate_prescription(request):
    """Generate e-prescription for student."""
    
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        student_profile = get_object_or_404(StudentProfile, student_id=student_id)
        
        # Create prescription
        from templates_docs.models import Prescription
        prescription = Prescription.objects.create(
            student=student_profile,
            doctor=request.user,
            diagnosis=request.POST.get('diagnosis', ''),
            medications=request.POST.get('medications', ''),
            instructions=request.POST.get('instructions', '')
        )
        
        # Generate PDF
        pdf_file = generate_prescription_pdf(prescription)
        prescription.pdf_file.save(
            f"prescription_{prescription.prescription_number}.pdf",
            pdf_file,
            save=True
        )
        
        messages.success(
            request,
            f'E-Prescription generated successfully! Rx No: {prescription.prescription_number}'
        )
        return redirect('doctors:templates')
    
    return render(request, 'doctor/generate-prescription.html')


@login_required
@doctor_required
def generate_clearance(request):
    """Generate medical clearance for student."""
    
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        student_profile = get_object_or_404(StudentProfile, student_id=student_id)
        
        form = CertificateGenerationForm(request.POST)
        if form.is_valid():
            certificate = form.save(commit=False)
            certificate.student = student_profile
            certificate.doctor = request.user
            certificate.title = "Medical Clearance"
            certificate.save()
            
            # Generate PDF
            pdf_file = generate_certificate_pdf(certificate)
            certificate.pdf_file.save(
                f"clearance_{certificate.certificate_number}.pdf",
                pdf_file,
                save=True
            )
            
            messages.success(
                request,
                f'Medical Clearance generated successfully! Certificate No: {certificate.certificate_number}'
            )
            return redirect('doctors:templates')
    
    return render(request, 'doctor/generate-clearance.html')


@login_required
@doctor_required
def generate_dental_certificate(request):
    """Generate dental certificate for student."""
    
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        student_profile = get_object_or_404(StudentProfile, student_id=student_id)
        
        form = CertificateGenerationForm(request.POST)
        if form.is_valid():
            certificate = form.save(commit=False)
            certificate.student = student_profile
            certificate.doctor = request.user
            certificate.title = "Dental Certificate"
            certificate.save()
            
            # Generate PDF
            pdf_file = generate_certificate_pdf(certificate)
            certificate.pdf_file.save(
                f"dental_{certificate.certificate_number}.pdf",
                pdf_file,
                save=True
            )
            
            messages.success(
                request,
                f'Dental Certificate generated successfully! Certificate No: {certificate.certificate_number}'
            )
            return redirect('doctors:templates')
    
    return render(request, 'doctor/generate-dental-certificate.html')


@login_required
@doctor_required
def student_lookup_api(request):
    """API endpoint to lookup student by ID (AJAX)."""
    
    student_id = request.GET.get('student_id', '').strip()
    
    if not student_id:
        return JsonResponse({'error': 'Student ID is required'}, status=400)
    
    try:
        student = StudentProfile.objects.select_related('user').get(student_id=student_id)
        
        data = {
            'success': True,
            'student': {
                'name': student.user.get_full_name(),
                'student_id': student.student_id,
                'age': student.get_age(),
                'sex': student.get_sex_display(),
                'program': student.get_program_display(),
                'year_level': student.get_year_level_display(),
                'course': f"{student.get_program_display()} - {student.get_year_level_display()}",
                'contact_number': student.contact_number,
                'blood_type': student.get_blood_type_display(),
                'allergies': student.allergies or 'None',
            }
        }
        return JsonResponse(data)
        
    except StudentProfile.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': f'No student found with ID: {student_id}'
        }, status=404)