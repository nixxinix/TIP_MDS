"""
Admin configuration for analytics models.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import MorbidityStatistic, ConsultationStatistic, GeneratedReport


@admin.register(MorbidityStatistic)
class MorbidityStatisticAdmin(admin.ModelAdmin):
    """Admin for MorbidityStatistic model."""
    
    list_display = [
        'diagnosis', 'record_type', 'case_count', 'percentage',
        'period_type', 'period_start', 'period_end', 'generated_at'
    ]
    list_filter = [
        'record_type', 'period_type', 'period_start', 'generated_at'
    ]
    search_fields = ['diagnosis']
    readonly_fields = ['id', 'generated_at']
    date_hierarchy = 'period_start'
    
    fieldsets = (
        ('Period Information', {
            'fields': ('period_type', 'period_start', 'period_end')
        }),
        ('Morbidity Data', {
            'fields': ('diagnosis', 'record_type', 'case_count', 'percentage')
        }),
        ('Metadata', {
            'fields': ('generated_by', 'generated_at')
        }),
    )


@admin.register(ConsultationStatistic)
class ConsultationStatisticAdmin(admin.ModelAdmin):
    """Admin for ConsultationStatistic model."""
    
    list_display = [
        'period_type', 'period_start', 'period_end',
        'total_consultations', 'medical_consultations', 'dental_consultations',
        'total_appointments', 'certificates_issued', 'generated_at'
    ]
    list_filter = ['period_type', 'period_start', 'generated_at']
    readonly_fields = ['id', 'generated_at']
    date_hierarchy = 'period_start'
    
    fieldsets = (
        ('Period Information', {
            'fields': ('period_type', 'period_start', 'period_end')
        }),
        ('Consultation Statistics', {
            'fields': (
                'total_consultations', 'medical_consultations', 'dental_consultations'
            )
        }),
        ('Appointment Statistics', {
            'fields': (
                'total_appointments', 'completed_appointments',
                'cancelled_appointments', 'no_show_appointments'
            )
        }),
        ('Documents Issued', {
            'fields': ('certificates_issued', 'prescriptions_issued')
        }),
        ('Student Registrations', {
            'fields': ('new_students_registered',)
        }),
        ('Metadata', {
            'fields': ('generated_at',)
        }),
    )


@admin.register(GeneratedReport)
class GeneratedReportAdmin(admin.ModelAdmin):
    """Admin for GeneratedReport model."""
    
    list_display = [
        'report_name', 'report_type', 'format',
        'date_from', 'date_to', 'generated_by',
        'download_count', 'generated_at', 'download_link'
    ]
    list_filter = ['report_type', 'format', 'generated_at']
    search_fields = ['report_name', 'generated_by__email']
    readonly_fields = ['id', 'generated_at', 'download_count', 'download_link']
    date_hierarchy = 'generated_at'
    
    fieldsets = (
        ('Report Information', {
            'fields': ('id', 'report_name', 'report_type', 'format')
        }),
        ('Date Range', {
            'fields': ('date_from', 'date_to')
        }),
        ('Report File', {
            'fields': ('report_file', 'download_link')
        }),
        ('Filters', {
            'fields': ('filters_applied',)
        }),
        ('Metadata', {
            'fields': ('generated_by', 'generated_at', 'download_count')
        }),
    )
    
    def download_link(self, obj):
        """Display download link."""
        if obj.report_file:
            return format_html(
                '<a href="{}" target="_blank" class="button">Download Report</a>',
                obj.report_file.url
            )
        return "No file"
    download_link.short_description = 'Download'