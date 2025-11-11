"""
Doctor models for TIP MDS EMR system.
Lightweight profile for medical/dental staff.
"""

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class DoctorProfile(models.Model):
    """
    Extended profile for doctor/staff users.
    Contains professional information.
    """
    
    SPECIALIZATION_CHOICES = (
        ('general_medicine', 'General Medicine'),
        ('general_dentistry', 'General Dentistry'),
        ('pediatrics', 'Pediatrics'),
        ('internal_medicine', 'Internal Medicine'),
        ('orthopedics', 'Orthopedics'),
        ('dermatology', 'Dermatology'),
        ('ophthalmology', 'Ophthalmology'),
        ('ent', 'ENT (Ear, Nose, Throat)'),
        ('orthodontics', 'Orthodontics'),
        ('oral_surgery', 'Oral Surgery'),
        ('other', 'Other'),
    )
    
    # Primary key and user relation
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='doctor_profile',
        primary_key=True
    )
    
    # Professional Information (nullable for first-time login)
    license_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        unique=True,
        help_text=_('Professional license number (PRC)')
    )
    
    specialization = models.CharField(
        max_length=50,
        choices=SPECIALIZATION_CHOICES,
        default='general_medicine',
        help_text=_('Medical/dental specialization')
    )
    
    department = models.CharField(
        max_length=100,
        help_text=_('Department or clinic'),
        default='Medical Services'
    )
    
    # Professional Details
    years_of_experience = models.PositiveIntegerField(
        default=0,
        help_text=_('Years of professional experience')
    )
    
    qualifications = models.TextField(
        blank=True,
        null=True,
        help_text=_('Educational background and certifications')
    )
    
    # Contact and Schedule
    office_location = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text=_('Office or clinic location')
    )
    
    consultation_hours = models.TextField(
        blank=True,
        null=True,
        help_text=_('Available consultation hours')
    )
    
    # Professional Signature (for certificates)
    signature_image = models.ImageField(
        upload_to='signatures/',
        blank=True,
        null=True,
        help_text=_('Digital signature for certificates')
    )
    
    # Status
    is_active = models.BooleanField(
        default=True,
        help_text=_('Whether doctor is currently active')
    )
    
    is_available_for_appointments = models.BooleanField(
        default=True,
        help_text=_('Whether doctor accepts new appointments')
    )
    
    # Track profile completion
    profile_completed = models.BooleanField(
        default=False,
        help_text=_('Whether doctor has completed their profile setup')
    )
    
    # Track if this is first login
    temp_password = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text=_('Temporary password for first login (plain text for display only)')
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('doctor profile')
        verbose_name_plural = _('doctor profiles')
        ordering = ['user__last_name', 'user__first_name']
        indexes = [
            models.Index(fields=['license_number']),
            models.Index(fields=['specialization']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"Dr. {self.user.get_full_name()} - {self.get_specialization_display()}"
    
    def get_full_title(self):
        """Return doctor's name with title."""
        return f"Dr. {self.user.get_full_name()}"
    
    def is_profile_complete(self):
        """Check if profile has required fields."""
        return bool(self.license_number and self.specialization)