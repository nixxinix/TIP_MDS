"""
Analytics models for TIP MDS EMR system.
Stores aggregated statistics and reports.
"""

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import uuid


class MorbidityStatistic(models.Model):
    """
    Aggregated morbidity statistics for a time period.
    Stores top diagnoses and their frequencies.
    """
    
    PERIOD_TYPE_CHOICES = (
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    )
    
    # Unique identifier
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    # Time Period
    period_type = models.CharField(
        max_length=10,
        choices=PERIOD_TYPE_CHOICES,
        help_text=_('Type of time period')
    )
    
    period_start = models.DateField(
        help_text=_('Start date of the period')
    )
    
    period_end = models.DateField(
        help_text=_('End date of the period')
    )
    
    # Statistics Data (stored as JSON-like text)
    diagnosis = models.CharField(
        max_length=500,
        help_text=_('Diagnosis or condition name')
    )
    
    record_type = models.CharField(
        max_length=10,
        choices=(('medical', 'Medical'), ('dental', 'Dental')),
        default='medical'
    )
    
    case_count = models.PositiveIntegerField(
        default=0,
        help_text=_('Number of cases for this diagnosis')
    )
    
    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text=_('Percentage of total cases')
    )
    
    # Metadata
    generated_at = models.DateTimeField(auto_now_add=True)
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role__in': ['doctor', 'admin']}
    )
    
    class Meta:
        verbose_name = _('morbidity statistic')
        verbose_name_plural = _('morbidity statistics')
        ordering = ['-period_start', '-case_count']
        indexes = [
            models.Index(fields=['period_type', 'period_start']),
            models.Index(fields=['diagnosis']),
            models.Index(fields=['record_type']),
        ]
        unique_together = [['period_type', 'period_start', 'diagnosis', 'record_type']]
    
    def __str__(self):
        return f"{self.diagnosis} - {self.case_count} cases ({self.period_type})"


class ConsultationStatistic(models.Model):
    """
    Daily/weekly/monthly consultation statistics.
    Tracks number of consultations and service types.
    """
    
    PERIOD_TYPE_CHOICES = (
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    )
    
    # Unique identifier
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    # Time Period
    period_type = models.CharField(
        max_length=10,
        choices=PERIOD_TYPE_CHOICES
    )
    
    period_start = models.DateField()
    period_end = models.DateField()
    
    # Consultation Counts
    total_consultations = models.PositiveIntegerField(
        default=0,
        help_text=_('Total number of consultations')
    )
    
    medical_consultations = models.PositiveIntegerField(
        default=0,
        help_text=_('Number of medical consultations')
    )
    
    dental_consultations = models.PositiveIntegerField(
        default=0,
        help_text=_('Number of dental consultations')
    )
    
    # Appointments
    total_appointments = models.PositiveIntegerField(
        default=0,
        help_text=_('Total appointments scheduled')
    )
    
    completed_appointments = models.PositiveIntegerField(
        default=0,
        help_text=_('Completed appointments')
    )
    
    cancelled_appointments = models.PositiveIntegerField(
        default=0,
        help_text=_('Cancelled appointments')
    )
    
    no_show_appointments = models.PositiveIntegerField(
        default=0,
        help_text=_('No-show appointments')
    )
    
    # Certificates Issued
    certificates_issued = models.PositiveIntegerField(
        default=0,
        help_text=_('Number of certificates issued')
    )
    
    prescriptions_issued = models.PositiveIntegerField(
        default=0,
        help_text=_('Number of prescriptions issued')
    )
    
    # New Students
    new_students_registered = models.PositiveIntegerField(
        default=0,
        help_text=_('New student registrations')
    )
    
    # Metadata
    generated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('consultation statistic')
        verbose_name_plural = _('consultation statistics')
        ordering = ['-period_start']
        indexes = [
            models.Index(fields=['period_type', 'period_start']),
        ]
        unique_together = [['period_type', 'period_start']]
    
    def __str__(self):
        return f"{self.period_type.title()} Stats - {self.period_start} ({self.total_consultations} consultations)"


class GeneratedReport(models.Model):
    """
    Tracks generated reports for download history.
    """
    
    REPORT_TYPE_CHOICES = (
        ('morbidity', 'Morbidity Report'),
        ('consultation', 'Consultation Report'),
        ('appointments', 'Appointments Report'),
        ('students', 'Student Registry Report'),
        ('certificates', 'Certificates Report'),
        ('custom', 'Custom Report'),
    )
    
    FORMAT_CHOICES = (
        ('pdf', 'PDF'),
        ('csv', 'CSV'),
        ('excel', 'Excel'),
    )
    
    # Unique identifier
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    # Report Details
    report_type = models.CharField(
        max_length=20,
        choices=REPORT_TYPE_CHOICES
    )
    
    report_name = models.CharField(
        max_length=200,
        help_text=_('Report title/name')
    )
    
    format = models.CharField(
        max_length=10,
        choices=FORMAT_CHOICES,
        default='pdf'
    )
    
    # Date Range
    date_from = models.DateField()
    date_to = models.DateField()
    
    # Report File
    report_file = models.FileField(
        upload_to='reports/%Y/%m/',
        help_text=_('Generated report file')
    )
    
    # Filters Applied (stored as JSON text)
    filters_applied = models.TextField(
        blank=True,
        null=True,
        help_text=_('JSON string of filters used')
    )
    
    # Metadata
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'role__in': ['doctor', 'admin']}
    )
    
    generated_at = models.DateTimeField(auto_now_add=True)
    
    download_count = models.PositiveIntegerField(
        default=0,
        help_text=_('Number of times downloaded')
    )
    
    class Meta:
        verbose_name = _('generated report')
        verbose_name_plural = _('generated reports')
        ordering = ['-generated_at']
        indexes = [
            models.Index(fields=['report_type', 'generated_at']),
            models.Index(fields=['generated_by']),
        ]
    
    def __str__(self):
        return f"{self.report_name} ({self.format.upper()}) - {self.generated_at.strftime('%Y-%m-%d')}"
    
    def increment_download(self):
        """Increment download counter."""
        self.download_count += 1
        self.save(update_fields=['download_count'])