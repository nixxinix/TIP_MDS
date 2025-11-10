"""
Templates and documents models for TIP MDS EMR system.
Handles certificate generation, prescriptions, and document templates.
"""

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from students.models import StudentProfile
import uuid


class Template(models.Model):
    """
    Document templates for certificates, prescriptions, etc.
    Uses HTML templates with placeholder variables.
    """
    
    TEMPLATE_TYPE_CHOICES = (
        ('medical_certificate', 'Medical Certificate'),
        ('dental_certificate', 'Dental Certificate'),
        ('medical_clearance', 'Medical Clearance'),
        ('health_certificate', 'Health Certificate'),
        ('prescription', 'E-Prescription'),
        ('lab_request', 'Laboratory Request'),
        ('referral', 'Referral Letter'),
        ('excuse_letter', 'Excuse Letter'),
        ('other', 'Other'),
    )
    
    # Unique identifier
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    # Template Information
    name = models.CharField(
        max_length=200,
        help_text=_('Template name for identification')
    )
    
    template_type = models.CharField(
        max_length=30,
        choices=TEMPLATE_TYPE_CHOICES,
        help_text=_('Type of document template')
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        help_text=_('Description of template usage')
    )
    
    # Template Content (HTML)
    template_html = models.TextField(
        help_text=_(
            'HTML template with placeholders. '
            'Use {{variable_name}} for dynamic content. '
            'Available variables: student_name, student_id, date, diagnosis, etc.'
        )
    )
    
    # CSS Styling
    template_css = models.TextField(
        blank=True,
        null=True,
        help_text=_('CSS styles for PDF generation')
    )
    
    # Header and Footer
    header_image = models.ImageField(
        upload_to='templates/headers/',
        blank=True,
        null=True,
        help_text=_('Header image/logo for template')
    )
    
    footer_text = models.TextField(
        blank=True,
        null=True,
        help_text=_('Footer text for template')
    )
    
    # Status
    is_active = models.BooleanField(
        default=True,
        help_text=_('Whether this template is currently in use')
    )
    
    is_default = models.BooleanField(
        default=False,
        help_text=_('Default template for this type')
    )
    
    # Metadata
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_templates',
        limit_choices_to={'role__in': ['doctor', 'admin']}
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('document template')
        verbose_name_plural = _('document templates')
        ordering = ['template_type', 'name']
        indexes = [
            models.Index(fields=['template_type', 'is_active']),
            models.Index(fields=['is_default']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_template_type_display()})"
    
    def get_available_variables(self):
        """Return list of available template variables."""
        return [
            'student_name', 'student_id', 'program', 'year_level',
            'date', 'date_issued', 'valid_until',
            'doctor_name', 'doctor_license', 'doctor_specialization',
            'diagnosis', 'prescription', 'remarks',
            'height', 'weight', 'blood_pressure', 'temperature',
            'certificate_number', 'school_name', 'school_address'
        ]


class IssuedCertificate(models.Model):
    """
    Issued certificates and documents.
    Stores generated PDFs and tracks validity.
    """
    
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('revoked', 'Revoked'),
    )
    
    # Unique identifier
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    # Certificate Number (for verification)
    certificate_number = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        help_text=_('Unique certificate number')
    )
    
    # Relations
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='issued_certificates'
    )
    
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='issued_certificates',
        limit_choices_to={'role__in': ['doctor', 'admin']}
    )
    
    template = models.ForeignKey(
        Template,
        on_delete=models.SET_NULL,
        null=True,
        related_name='issued_documents'
    )
    
    # Certificate Details
    title = models.CharField(
        max_length=200,
        help_text=_('Certificate title/subject')
    )
    
    purpose = models.TextField(
        blank=True,
        null=True,
        help_text=_('Purpose of certificate')
    )
    
    diagnosis = models.TextField(
        blank=True,
        null=True,
        help_text=_('Diagnosis or medical condition')
    )
    
    prescription = models.TextField(
        blank=True,
        null=True,
        help_text=_('Prescribed medications')
    )
    
    remarks = models.TextField(
        blank=True,
        null=True,
        help_text=_('Additional remarks or instructions')
    )
    
    # Validity
    date_issued = models.DateField(
        default=timezone.now,
        help_text=_('Date certificate was issued')
    )
    
    valid_until = models.DateField(
        blank=True,
        null=True,
        help_text=_('Expiration date of certificate')
    )
    
    # Generated PDF
    pdf_file = models.FileField(
        upload_to='certificates/%Y/%m/',
        blank=True,
        null=True,
        help_text=_('Generated PDF file')
    )
    
    # Status
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='active',
        help_text=_('Certificate status')
    )
    
    revoked_at = models.DateTimeField(
        blank=True,
        null=True
    )
    
    revocation_reason = models.TextField(
        blank=True,
        null=True,
        help_text=_('Reason for revocation')
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('issued certificate')
        verbose_name_plural = _('issued certificates')
        ordering = ['-date_issued', '-created_at']
        indexes = [
            models.Index(fields=['certificate_number']),
            models.Index(fields=['student', 'status']),
            models.Index(fields=['date_issued', 'status']),
            models.Index(fields=['valid_until']),
        ]
    
    def __str__(self):
        return f"{self.certificate_number} - {self.title}"
    
    def save(self, *args, **kwargs):
        """Generate certificate number on creation."""
        if not self.certificate_number:
            self.certificate_number = self.generate_certificate_number()
        super().save(*args, **kwargs)
    
    @staticmethod
    def generate_certificate_number():
        """Generate unique certificate number (e.g., CERT-2025-ABC123)."""
        import random
        import string
        
        year = timezone.now().year
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        cert_num = f"CERT-{year}-{random_part}"
        
        # Ensure uniqueness
        while IssuedCertificate.objects.filter(certificate_number=cert_num).exists():
            random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            cert_num = f"CERT-{year}-{random_part}"
        
        return cert_num
    
    def is_valid(self):
        """Check if certificate is still valid."""
        if self.status != 'active':
            return False
        
        if self.valid_until:
            return timezone.now().date() <= self.valid_until
        
        return True
    
    def revoke(self, reason=''):
        """Revoke the certificate."""
        self.status = 'revoked'
        self.revoked_at = timezone.now()
        self.revocation_reason = reason
        self.save()
    
    def check_expiry(self):
        """Check and update expiry status."""
        if self.valid_until and timezone.now().date() > self.valid_until:
            if self.status == 'active':
                self.status = 'expired'
                self.save()
                return True
        return False


class Prescription(models.Model):
    """
    Electronic prescriptions issued by doctors.
    """
    
    # Unique identifier
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    # Prescription Number
    prescription_number = models.CharField(
        max_length=50,
        unique=True,
        editable=False
    )
    
    # Relations
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='prescriptions'
    )
    
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='prescriptions_issued',
        limit_choices_to={'role__in': ['doctor', 'admin']}
    )
    
    # Prescription Details
    diagnosis = models.TextField(
        help_text=_('Diagnosis or condition')
    )
    
    medications = models.TextField(
        help_text=_(
            'List of medications with dosage and frequency. '
            'Format: Drug name - Dosage - Frequency - Duration'
        )
    )
    
    instructions = models.TextField(
        blank=True,
        null=True,
        help_text=_('Special instructions for patient')
    )
    
    # Validity
    date_issued = models.DateField(default=timezone.now)
    
    valid_until = models.DateField(
        blank=True,
        null=True,
        help_text=_('Prescription validity period')
    )
    
    # PDF
    pdf_file = models.FileField(
        upload_to='prescriptions/%Y/%m/',
        blank=True,
        null=True
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('prescription')
        verbose_name_plural = _('prescriptions')
        ordering = ['-date_issued', '-created_at']
        indexes = [
            models.Index(fields=['prescription_number']),
            models.Index(fields=['student', 'date_issued']),
        ]
    
    def __str__(self):
        return f"{self.prescription_number} - {self.student.student_id}"
    
    def save(self, *args, **kwargs):
        """Generate prescription number on creation."""
        if not self.prescription_number:
            self.prescription_number = self.generate_prescription_number()
        super().save(*args, **kwargs)
    
    @staticmethod
    def generate_prescription_number():
        """Generate unique prescription number."""
        import random
        import string
        
        year = timezone.now().year
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        rx_num = f"RX-{year}-{random_part}"
        
        while Prescription.objects.filter(prescription_number=rx_num).exists():
            random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            rx_num = f"RX-{year}-{random_part}"
        
        return rx_num