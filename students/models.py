"""
Student models for TIP MDS EMR system.
Handles student profiles, medical records, and update requests.
"""

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta
import uuid


class StudentProfile(models.Model):
    """
    Extended profile for student users.
    Contains academic and medical information.
    """
    
    PROGRAM_CHOICES = (
        ('CS', 'Computer Science'),
        ('IT', 'Information Technology'),
        ('CE', 'Computer Engineering'),
        ('EE', 'Electrical Engineering'),
        ('ME', 'Mechanical Engineering'),
        ('IE', 'Industrial Engineering'),
        ('ARCH', 'Architecture'),
        ('BA', 'Business Administration'),
        ('ACCT', 'Accountancy'),
        ('OTHER', 'Other'),
    )
    
    YEAR_LEVEL_CHOICES = (
        ('1', '1st Year'),
        ('2', '2nd Year'),
        ('3', '3rd Year'),
        ('4', '4th Year'),
        ('5', '5th Year'),
    )
    
    SEX_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )
    
    BLOOD_TYPE_CHOICES = (
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
        ('UNKNOWN', 'Unknown'),
    )
    
    # Primary key and user relation
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_profile',
        primary_key=True
    )
    
    # Academic Information
    student_id = models.CharField(
        max_length=20,
        unique=True,
        help_text=_('Unique student ID number')
    )
    
    program = models.CharField(
        max_length=10,
        choices=PROGRAM_CHOICES,
        help_text=_('Academic program/course')
    )
    
    year_level = models.CharField(
        max_length=1,
        choices=YEAR_LEVEL_CHOICES,
        help_text=_('Current year level')
    )
    
    # Personal Information
    sex = models.CharField(
        max_length=1,
        choices=SEX_CHOICES
    )
    
    date_of_birth = models.DateField(
        help_text=_('Date of birth')
    )
    
    contact_number = models.CharField(
        max_length=20,
        help_text=_('Primary contact number')
    )
    
    address = models.TextField(
        help_text=_('Complete address')
    )
    
    # Emergency Contact
    emergency_contact_name = models.CharField(
        max_length=200,
        help_text=_('Name of emergency contact person')
    )
    
    emergency_contact_relationship = models.CharField(
        max_length=100,
        help_text=_('Relationship to emergency contact')
    )
    
    emergency_contact_number = models.CharField(
        max_length=20,
        help_text=_('Emergency contact phone number')
    )
    
    emergency_contact_address = models.TextField(
        blank=True,
        null=True,
        help_text=_('Emergency contact address')
    )
    
    # Medical Information
    height_cm = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(50), MaxValueValidator(300)],
        blank=True,
        null=True,
        help_text=_('Height in centimeters')
    )
    
    weight_kg = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(20), MaxValueValidator(300)],
        blank=True,
        null=True,
        help_text=_('Weight in kilograms')
    )
    
    blood_type = models.CharField(
        max_length=10,
        choices=BLOOD_TYPE_CHOICES,
        default='UNKNOWN',
        help_text=_('Blood type')
    )
    
    allergies = models.TextField(
        blank=True,
        null=True,
        help_text=_('Known allergies (comma-separated)')
    )
    
    current_medications = models.TextField(
        blank=True,
        null=True,
        help_text=_('Current medications being taken')
    )
    
    immunization_history = models.TextField(
        blank=True,
        null=True,
        help_text=_('Immunization and vaccination history')
    )
    
    medical_history = models.TextField(
        blank=True,
        null=True,
        help_text=_('Past medical conditions and surgeries')
    )
    
    # Dental Information
    last_dental_visit = models.DateField(
        blank=True,
        null=True,
        help_text=_('Date of last dental visit')
    )
    
    oral_habits = models.TextField(
        blank=True,
        null=True,
        help_text=_('Oral habits (e.g., teeth grinding, smoking)')
    )
    
    dental_history = models.TextField(
        blank=True,
        null=True,
        help_text=_('Previous dental procedures and concerns')
    )
    
    # Status and Timestamps
    is_complete = models.BooleanField(
        default=False,
        help_text=_('Whether profile is complete')
    )
    
    is_verified = models.BooleanField(
        default=False,
        help_text=_('Whether profile has been verified by staff')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('student profile')
        verbose_name_plural = _('student profiles')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['student_id']),
            models.Index(fields=['program', 'year_level']),
            models.Index(fields=['is_verified']),
        ]
    
    def __str__(self):
        return f"{self.student_id} - {self.user.get_full_name()}"
    
    def get_age(self):
        """Calculate age from date of birth."""
        today = timezone.now().date()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )
    
    def get_bmi(self):
        """Calculate BMI if height and weight are available."""
        if self.height_cm and self.weight_kg:
            height_m = float(self.height_cm) / 100
            return float(self.weight_kg) / (height_m ** 2)
        return None
    
    def check_completion(self):
        """Check if profile is complete."""
        required_fields = [
            self.student_id, self.program, self.year_level,
            self.sex, self.date_of_birth, self.contact_number,
            self.address, self.emergency_contact_name,
            self.emergency_contact_number
        ]
        self.is_complete = all(required_fields)
        return self.is_complete


class MedicalRecord(models.Model):
    """
    Medical and dental records for students.
    Created by doctors after consultations.
    """
    
    RECORD_TYPE_CHOICES = (
        ('medical', 'Medical'),
        ('dental', 'Dental'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
    )
    
    # Unique identifier
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    # Relations
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='medical_records'
    )
    
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_records',
        limit_choices_to={'role__in': ['doctor', 'admin']}
    )
    
    # Record Details
    record_type = models.CharField(
        max_length=10,
        choices=RECORD_TYPE_CHOICES,
        default='medical'
    )
    
    visit_date = models.DateField(
        default=timezone.now,
        help_text=_('Date of consultation/visit')
    )
    
    chief_complaint = models.TextField(
        help_text=_('Main reason for visit')
    )
    
    diagnosis = models.TextField(
        help_text=_('Diagnosis or findings')
    )
    
    procedure = models.TextField(
        blank=True,
        null=True,
        help_text=_('Procedures performed')
    )
    
    prescription = models.TextField(
        blank=True,
        null=True,
        help_text=_('Medications prescribed')
    )
    
    remarks = models.TextField(
        blank=True,
        null=True,
        help_text=_('Additional notes and observations')
    )
    
    # Vital Signs (for medical records)
    blood_pressure = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text=_('Blood pressure (e.g., 120/80)')
    )
    
    temperature = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        blank=True,
        null=True,
        help_text=_('Temperature in Celsius')
    )
    
    pulse_rate = models.IntegerField(
        blank=True,
        null=True,
        help_text=_('Pulse rate (bpm)')
    )
    
    respiratory_rate = models.IntegerField(
        blank=True,
        null=True,
        help_text=_('Respiratory rate (breaths per minute)')
    )
    
    # File Attachments
    lab_results = models.FileField(
        upload_to='medical_records/lab_results/%Y/%m/',
        blank=True,
        null=True,
        help_text=_('Laboratory results (PDF, images)')
    )
    
    xray_image = models.ImageField(
        upload_to='medical_records/xrays/%Y/%m/',
        blank=True,
        null=True,
        help_text=_('X-ray or dental images')
    )
    
    attachments = models.FileField(
        upload_to='medical_records/attachments/%Y/%m/',
        blank=True,
        null=True,
        help_text=_('Other supporting documents')
    )
    
    # Status and Approval
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='approved',
        help_text=_('Record approval status')
    )
    
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_records',
        limit_choices_to={'role__in': ['doctor', 'admin']}
    )
    
    approved_at = models.DateTimeField(
        blank=True,
        null=True
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('medical record')
        verbose_name_plural = _('medical records')
        ordering = ['-visit_date', '-created_at']
        indexes = [
            models.Index(fields=['student', 'record_type']),
            models.Index(fields=['status', 'visit_date']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_record_type_display()} - {self.student.student_id} - {self.visit_date}"
    
    def approve(self, approved_by_user):
        """Approve the medical record."""
        self.status = 'approved'
        self.approved_by = approved_by_user
        self.approved_at = timezone.now()
        self.save()
    
    def decline(self):
        """Decline the medical record."""
        self.status = 'declined'
        self.save()


class RecordUpdateRequest(models.Model):
    """
    Student requests to update their profile information.
    Requires approval from doctor/admin within 7 days.
    """
    
    STATUS_CHOICES = (
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
        ('expired', 'Expired'),
    )
    
    # Unique identifier
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    # Relations
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='update_requests'
    )
    
    # Request Data (JSON fields store old and new values)
    field_name = models.CharField(
        max_length=100,
        help_text=_('Name of field being updated')
    )
    
    old_value = models.TextField(
        blank=True,
        null=True,
        help_text=_('Previous value')
    )
    
    new_value = models.TextField(
        help_text=_('New requested value')
    )
    
    reason = models.TextField(
        help_text=_('Reason for update request')
    )
    
    supporting_document = models.FileField(
        upload_to='update_requests/documents/%Y/%m/',
        blank=True,
        null=True,
        help_text=_('Supporting documents (medical certificates, etc.)')
    )
    
    # Status and Approval
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_requests',
        limit_choices_to={'role__in': ['doctor', 'admin']}
    )
    
    review_notes = models.TextField(
        blank=True,
        null=True,
        help_text=_('Notes from reviewer')
    )
    
    reviewed_at = models.DateTimeField(
        blank=True,
        null=True
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField(
        help_text=_('Request expires after 7 days')
    )
    
    class Meta:
        verbose_name = _('update request')
        verbose_name_plural = _('update requests')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['student', 'status']),
            models.Index(fields=['status', 'expiry_date']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Update Request - {self.student.student_id} - {self.field_name}"
    
    def save(self, *args, **kwargs):
        """Set expiry date on creation (7 days from now)."""
        if not self.expiry_date:
            self.expiry_date = timezone.now() + timedelta(days=7)
        super().save(*args, **kwargs)
    
    def is_expired(self):
        """Check if request has expired."""
        return timezone.now() > self.expiry_date and self.status == 'pending'
    
    def check_and_mark_expired(self):
        """Mark as expired if past expiry date."""
        if self.is_expired():
            self.status = 'expired'
            self.save()
            return True
        return False
    
    def approve(self, reviewed_by_user, apply_changes=True):
        """
        Approve the update request and optionally apply changes.
        
        Args:
            reviewed_by_user: User who approved the request
            apply_changes: Whether to apply changes to student profile
        """
        self.status = 'approved'
        self.reviewed_by = reviewed_by_user
        self.reviewed_at = timezone.now()
        
        if apply_changes:
            # Apply the change to student profile
            setattr(self.student, self.field_name, self.new_value)
            self.student.save()
        
        self.save()
    
    def decline(self, reviewed_by_user, notes=''):
        """Decline the update request."""
        self.status = 'declined'
        self.reviewed_by = reviewed_by_user
        self.reviewed_at = timezone.now()
        self.review_notes = notes
        self.save()