"""
Views for student portal.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.http import JsonResponse
from accounts.decorators import student_required
from .models import StudentProfile, MedicalRecord, RecordUpdateRequest
from .forms import StudentRegistrationForm, StudentUpdateForm, RecordUpdateRequestForm
from appointments.models import Appointment
from templates_docs.models import IssuedCertificate, Prescription


@login_required
@student_required
def student_dashboard(request):
    """Student dashboard view."""
    
    # Get or create student profile
    try:
        student_profile = request.user.student_profile
    except StudentProfile.DoesNotExist:
        # Redirect to registration if profile doesn't exist
        messages.warning(request, 'Please complete your registration first.')
        return redirect('students:register')
    
    # Get statistics
    total_records = MedicalRecord.objects.filter(
        student=student_profile,
        status='approved'
    ).count()
    
    pending_requests = RecordUpdateRequest.objects.filter(
        student=student_profile,
        status='pending'
    ).count()
    
    appointments_count = Appointment.objects.filter(
        student=student_profile
    ).count()
    
    approved_records = MedicalRecord.objects.filter(
        student=student_profile,
        status='approved'
    ).count()
    
    # Recent records
    recent_records = MedicalRecord.objects.filter(
        student=student_profile,
        status='approved'
    ).select_related('doctor').order_by('-visit_date')[:5]
    
    # Upcoming appointments
    upcoming_appointments = Appointment.objects.filter(
        student=student_profile,
        status__in=['pending', 'approved']
    ).select_related('doctor').order_by('preferred_date')[:5]
    
    # Recent notifications
    from notifications.models import Notification
    notifications = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).order_by('-created_at')[:5]
    
    context = {
        'student_profile': student_profile,
        'total_records': total_records,
        'pending_requests': pending_requests,
        'appointments_count': appointments_count,
        'approved_records': approved_records,
        'recent_records': recent_records,
        'upcoming_appointments': upcoming_appointments,
        'notifications': notifications,
    }
    
    return render(request, 'student/student-dashboard.html', context)


@login_required
def student_registration(request):
    """New student registration form."""
    
    # Check if already has profile
    if hasattr(request.user, 'student_profile'):
        messages.info(request, 'You already have a registered profile.')
        return redirect('students:dashboard')
    
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.check_completion()
            profile.save()
            
            messages.success(request, 'Registration completed successfully!')
            return redirect('students:dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = StudentRegistrationForm()
    
    context = {'form': form}
    return render(request, 'student/student-registration.html', context)


@login_required
@student_required
def student_update(request):
    """Student information update form."""
    
    student_profile = get_object_or_404(StudentProfile, user=request.user)
    
    if request.method == 'POST':
        form = StudentUpdateForm(request.POST, instance=student_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('students:dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = StudentUpdateForm(instance=student_profile)
    
    context = {
        'form': form,
        'student_profile': student_profile
    }
    return render(request, 'student/student-update.html', context)


@login_required
@student_required
def student_records(request):
    """View medical and dental records."""
    
    student_profile = get_object_or_404(StudentProfile, user=request.user)
    
    # Get approved records
    approved_records = MedicalRecord.objects.filter(
        student=student_profile,
        status='approved'
    ).select_related('doctor').order_by('-visit_date')
    
    # Get pending update requests
    pending_requests = RecordUpdateRequest.objects.filter(
        student=student_profile,
        status='pending'
    ).order_by('-created_at')
    
    context = {
        'student_profile': student_profile,
        'approved_records': approved_records,
        'pending_requests': pending_requests,
    }
    
    return render(request, 'student/student-records.html', context)


@login_required
@student_required
def record_detail(request, record_id):
    """View single medical record detail."""
    
    student_profile = get_object_or_404(StudentProfile, user=request.user)
    record = get_object_or_404(
        MedicalRecord,
        id=record_id,
        student=student_profile
    )
    
    context = {
        'record': record,
        'student_profile': student_profile
    }
    
    return render(request, 'student/record-detail.html', context)


@login_required
@student_required
def student_appointments(request):
    """View and manage appointments."""
    
    from appointments.forms import AppointmentBookingForm
    
    student_profile = get_object_or_404(StudentProfile, user=request.user)
    
    if request.method == 'POST':
        form = AppointmentBookingForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.student = student_profile
            appointment.save()
            
            messages.success(
                request,
                f'Appointment request submitted! Your ticket number is {appointment.ticket_number}'
            )
            return redirect('students:appointments')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AppointmentBookingForm()
    
    # Get appointments
    appointments = Appointment.objects.filter(
        student=student_profile
    ).select_related('doctor').order_by('-created_at')
    
    context = {
        'form': form,
        'appointments': appointments,
        'student_profile': student_profile
    }
    
    return render(request, 'student/student-appointments.html', context)


@login_required
@student_required
def appointment_detail(request, appointment_id):
    """View appointment details."""
    
    student_profile = get_object_or_404(StudentProfile, user=request.user)
    appointment = get_object_or_404(
        Appointment,
        id=appointment_id,
        student=student_profile
    )
    
    context = {
        'appointment': appointment,
        'student_profile': student_profile
    }
    
    return render(request, 'student/appointment-detail.html', context)


@login_required
@student_required
def cancel_appointment(request, appointment_id):
    """Cancel an appointment."""
    
    student_profile = get_object_or_404(StudentProfile, user=request.user)
    appointment = get_object_or_404(
        Appointment,
        id=appointment_id,
        student=student_profile
    )
    
    if appointment.status in ['pending', 'approved']:
        if request.method == 'POST':
            reason = request.POST.get('reason', 'Cancelled by student')
            appointment.cancel(reason=reason)
            messages.success(request, 'Appointment cancelled successfully.')
            return redirect('students:appointments')
    else:
        messages.error(request, 'This appointment cannot be cancelled.')
        return redirect('students:appointments')
    
    context = {'appointment': appointment}
    return render(request, 'student/cancel-appointment.html', context)


@login_required
@student_required
def student_certificates(request):
    """View issued certificates."""
    
    student_profile = get_object_or_404(StudentProfile, user=request.user)
    
    certificates = IssuedCertificate.objects.filter(
        student=student_profile
    ).select_related('doctor', 'template').order_by('-date_issued')
    
    prescriptions = Prescription.objects.filter(
        student=student_profile
    ).select_related('doctor').order_by('-date_issued')
    
    context = {
        'certificates': certificates,
        'prescriptions': prescriptions,
        'student_profile': student_profile
    }
    
    return render(request, 'student/student-certificates.html', context)


@login_required
@student_required
def request_update(request):
    """Request to update medical information."""
    
    student_profile = get_object_or_404(StudentProfile, user=request.user)
    
    if request.method == 'POST':
        form = RecordUpdateRequestForm(
            request.POST,
            request.FILES,
            student_profile=student_profile
        )
        if form.is_valid():
            update_request = form.save(commit=False)
            update_request.student = student_profile
            update_request.save()
            
            messages.success(
                request,
                'Update request submitted successfully. It will be reviewed within 7 days.'
            )
            return redirect('students:records')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RecordUpdateRequestForm(student_profile=student_profile)
    
    context = {
        'form': form,
        'student_profile': student_profile
    }
    
    return render(request, 'student/request-update.html', context)