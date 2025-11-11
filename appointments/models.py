"""
Appointment models for TIP MDS EMR system.
Handles appointment scheduling and management.
"""

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from students.models import StudentProfile
import uuid
import random
import string


class Appointment(models.Model):
    """
    Appointment booking system for medical and dental services.
    """
    
    SERVICE_TYPE_CHOICES = (
        ('medical_consultation', 'Medical Consultation'),
        ('dental_cleaning', 'Dental Cleaning'),
        ('dental_filling', 'Dental Filling'),
        ('dental_extraction', 'Dental Extraction'),
        ('medical_clearance', 'Medical Clearance'),
        ('health_certificate', 'Health Certificate'),
        ('vaccination', 'Vaccination'),
        ('physical_exam', 'Physical Examination'),
        ('follow_up', 'Follow-up Consultation'),
        ('emergency', 'Emergency'),
        ('other', 'Other'),
    )
    
    TIME_SLOT_CHOICES = (
        ('morning', 'Morning (8:00 AM - 12:00 PM)'),
        ('afternoon', 'Afternoon (1:00 PM - 5:00 PM)'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending Approval'),
        ('approved', 'Approved/Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    )
    
    # Unique identifier
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    # Ticket number for easy reference
    ticket_number = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        help_text=_('Unique ticket number for appointment')
    )
    
    # Relations
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='appointments'
    )
    
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_appointments',
        limit_choices_to={'role__in': ['doctor', 'admin']},
        help_text=_('Assigned doctor (set upon approval)')
    )
    
    # Appointment Details
    service_type = models.CharField(
        max_length=30,
        choices=SERVICE_TYPE_CHOICES,
        help_text=_('Type of service requested')
    )
    
    preferred_date = models.DateField(
        help_text=_('Preferred appointment date')
    )
    
    preferred_time_slot = models.CharField(
        max_length=10,
        choices=TIME_SLOT_CHOICES,
        default='morning',
        help_text=_('Preferred time slot')
    )
    
    actual_datetime = models.DateTimeField(
        blank=True,
        null=True,
        help_text=_('Actual scheduled date and time (set by doctor)')
    )
    
    # Reason and Notes
    reason = models.TextField(
        help_text=_('Reason for appointment / Chief complaint')
    )
    
    doctor_notes = models.TextField(
        blank=True,
        null=True,
        help_text=_('Notes from doctor')
    )
    
    # Emergency Contact for Appointment
    emergency_contact_name = models.CharField(
        max_length=200,
        help_text=_('Emergency contact name')
    )
    
    emergency_contact_number = models.CharField(
        max_length=20,
        help_text=_('Emergency contact number')
    )
    
    # Status and Management
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='pending',
        help_text=_('Appointment status')
    )
    
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_appointments',
        limit_choices_to={'role__in': ['doctor', 'admin']}
    )
    
    approved_at = models.DateTimeField(
        blank=True,
        null=True
    )
    
    completed_at = models.DateTimeField(
        blank=True,
        null=True
    )
    
    cancelled_at = models.DateTimeField(
        blank=True,
        null=True
    )
    
    cancelled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cancelled_appointments_by',
        help_text=_('User who cancelled the appointment')
    )
    
    cancellation_reason = models.TextField(
        blank=True,
        null=True,
        help_text=_('Reason for cancellation')
    )
    
    # Notifications
    reminder_sent = models.BooleanField(
        default=False,
        help_text=_('Whether reminder notification was sent')
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('appointment')
        verbose_name_plural = _('appointments')
        ordering = ['-preferred_date', '-created_at']
        indexes = [
            models.Index(fields=['student', 'status']),
            models.Index(fields=['doctor', 'status']),
            models.Index(fields=['preferred_date', 'status']),
            models.Index(fields=['ticket_number']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.ticket_number} - {self.student.student_id} - {self.get_service_type_display()}"
    
    def save(self, *args, **kwargs):
        """Generate ticket number on creation."""
        if not self.ticket_number:
            self.ticket_number = self.generate_ticket_number()
        super().save(*args, **kwargs)
    
    @staticmethod
    def generate_ticket_number():
        """Generate unique ticket number (e.g., APT-2025-ABC123)."""
        year = timezone.now().year
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        ticket = f"APT-{year}-{random_part}"
        
        # Ensure uniqueness
        while Appointment.objects.filter(ticket_number=ticket).exists():
            random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            ticket = f"APT-{year}-{random_part}"
        
        return ticket
    
    def approve(self, approved_by_user, doctor=None, actual_datetime=None):
        """
        Approve the appointment.
        
        Args:
            approved_by_user: User who approved the appointment
            doctor: Doctor to assign (optional)
            actual_datetime: Scheduled datetime (optional)
        """
        self.status = 'approved'
        self.approved_by = approved_by_user
        self.approved_at = timezone.now()
        
        if doctor:
            self.doctor = doctor
        
        if actual_datetime:
            self.actual_datetime = actual_datetime
        
        self.save()
    
    def complete(self):
        """Mark appointment as completed."""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()
    
    def cancel(self, reason='', cancelled_by=None):
        """Cancel the appointment."""
        self.status = 'cancelled'
        self.cancelled_at = timezone.now()
        self.cancellation_reason = reason
        if cancelled_by:
            self.cancelled_by = cancelled_by
        self.save()
    
    def mark_no_show(self):
        """Mark appointment as no show."""
        self.status = 'no_show'
        self.save()
    
    def is_upcoming(self):
        """Check if appointment is upcoming."""
        if self.status == 'approved' and self.preferred_date:
            return self.preferred_date >= timezone.now().date()
        return False
    
    def is_overdue(self):
        """Check if appointment date has passed but not completed."""
        if self.status in ['pending', 'approved'] and self.preferred_date:
            return self.preferred_date < timezone.now().date()
        return False


class AppointmentNote(models.Model):
    """
    Notes and comments on appointments.
    Can be added by doctors or admins.
    """
    
    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        related_name='notes'
    )
    
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'role__in': ['doctor', 'admin']}
    )
    
    note = models.TextField(
        help_text=_('Note or comment')
    )
    
    is_internal = models.BooleanField(
        default=False,
        help_text=_('Internal note (not visible to student)')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('appointment note')
        verbose_name_plural = _('appointment notes')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Note on {self.appointment.ticket_number} by {self.author}"