"""
Admin configuration for templates and documents.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Template, IssuedCertificate, Prescription


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    """Admin for Template model."""
    
    list_display = [
        'name', 'template_type', 'is_active', 'is_default',
        'created_by', 'created_at'
    ]
    list_filter = ['template_type', 'is_active', 'is_default', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at', 'preview_variables']
    
    fieldsets = (
        ('Template Information', {
            'fields': ('id', 'name', 'template_type', 'description')
        }),
        ('Template Content', {
            'fields': ('template_html', 'template_css')
        }),
        ('Header & Footer', {
            'fields': ('header_image', 'footer_text')
        }),
        ('Settings', {
            'fields': ('is_active', 'is_default')
        }),
        ('Available Variables', {
            'fields': ('preview_variables',),
            'description': 'Use these variables in your template with {{variable_name}} syntax'
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )
    
    def preview_variables(self, obj):
        """Display available template variables."""
        variables = obj.get_available_variables()
        html = '<ul style="column-count: 3;">'
        for var in variables:
            html += f'<li><code>{{{{{var}}}}}</code></li>'
        html += '</ul>'
        return mark_safe(html)
    preview_variables.short_description = 'Available Variables'
    
    def save_model(self, request, obj, form, change):
        """Set created_by on creation."""
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(IssuedCertificate)
class IssuedCertificateAdmin(admin.ModelAdmin):
    """Admin for IssuedCertificate model."""
    
    list_display = [
        'certificate_number', 'get_student_id', 'get_student_name',
        'title', 'status_badge', 'date_issued', 'valid_until',
        'is_valid_display', 'doctor'
    ]
    list_filter = ['status', 'date_issued', 'valid_until', 'created_at']
    search_fields = [
        'certificate_number', 'student__student_id',
        'student__user__first_name', 'student__user__last_name',
        'title'
    ]
    readonly_fields = [
        'id', 'certificate_number', 'created_at', 'updated_at',
        'revoked_at', 'pdf_preview'
    ]
    date_hierarchy = 'date_issued'
    
    fieldsets = (
        ('Certificate Information', {
            'fields': ('id', 'certificate_number', 'student', 'doctor', 'template')
        }),
        ('Certificate Details', {
            'fields': ('title', 'purpose', 'diagnosis', 'prescription', 'remarks')
        }),
        ('Validity', {
            'fields': ('date_issued', 'valid_until')
        }),
        ('PDF Document', {
            'fields': ('pdf_file', 'pdf_preview')
        }),
        ('Status', {
            'fields': ('status', 'revoked_at', 'revocation_reason')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def get_student_id(self, obj):
        """Display student ID."""
        return obj.student.student_id
    get_student_id.short_description = 'Student ID'
    get_student_id.admin_order_field = 'student__student_id'
    
    def get_student_name(self, obj):
        """Display student name."""
        return obj.student.user.get_full_name()
    get_student_name.short_description = 'Student Name'
    
    def status_badge(self, obj):
        """Display colored status badge."""
        colors = {
            'active': '#28a745',
            'expired': '#ffc107',
            'revoked': '#dc3545',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def is_valid_display(self, obj):
        """Display if certificate is valid."""
        if obj.is_valid():
            return format_html('<span style="color: green;">✓ Valid</span>')
        return format_html('<span style="color: red;">✗ Invalid</span>')
    is_valid_display.short_description = 'Validity'
    
    def pdf_preview(self, obj):
        """Display PDF download link."""
        if obj.pdf_file:
            return format_html(
                '<a href="{}" target="_blank" class="button">Download PDF</a>',
                obj.pdf_file.url
            )
        return "No PDF generated"
    pdf_preview.short_description = 'PDF File'
    
    actions = ['revoke_certificates', 'check_expiry']
    
    def revoke_certificates(self, request, queryset):
        """Bulk revoke selected certificates."""
        count = 0
        for cert in queryset.filter(status='active'):
            cert.revoke(reason='Revoked by admin')
            count += 1
        
        self.message_user(request, f'{count} certificate(s) revoked.')
    revoke_certificates.short_description = 'Revoke selected certificates'
    
    def check_expiry(self, request, queryset):
        """Check and update expiry status."""
        count = 0
        for cert in queryset:
            if cert.check_expiry():
                count += 1
        
        self.message_user(request, f'{count} certificate(s) marked as expired.')
    check_expiry.short_description = 'Check expiry status'


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    """Admin for Prescription model."""
    
    list_display = [
        'prescription_number', 'get_student_id', 'get_student_name',
        'date_issued', 'valid_until', 'doctor'
    ]
    list_filter = ['date_issued', 'valid_until', 'created_at']
    search_fields = [
        'prescription_number', 'student__student_id',
        'student__user__first_name', 'student__user__last_name',
        'diagnosis'
    ]
    readonly_fields = [
        'id', 'prescription_number', 'created_at', 'updated_at',
        'pdf_preview'
    ]
    date_hierarchy = 'date_issued'
    
    fieldsets = (
        ('Prescription Information', {
            'fields': ('id', 'prescription_number', 'student', 'doctor')
        }),
        ('Medical Details', {
            'fields': ('diagnosis', 'medications', 'instructions')
        }),
        ('Validity', {
            'fields': ('date_issued', 'valid_until')
        }),
        ('PDF Document', {
            'fields': ('pdf_file', 'pdf_preview')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def get_student_id(self, obj):
        """Display student ID."""
        return obj.student.student_id
    get_student_id.short_description = 'Student ID'
    get_student_id.admin_order_field = 'student__student_id'
    
    def get_student_name(self, obj):
        """Display student name."""
        return obj.student.user.get_full_name()
    get_student_name.short_description = 'Student Name'
    
    def pdf_preview(self, obj):
        """Display PDF download link."""
        if obj.pdf_file:
            return format_html(
                '<a href="{}" target="_blank" class="button">Download PDF</a>',
                obj.pdf_file.url
            )
        return "No PDF generated"
    pdf_preview.short_description = 'PDF File'