"""
Admin configuration for student models.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import StudentProfile, MedicalRecord, RecordUpdateRequest


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    """Admin for StudentProfile model."""
    
    list_display = [
        'student_id', 'get_full_name', 'program', 'year_level',
        'is_complete', 'is_verified', 'created_at'
    ]
    list_filter = ['program', 'year_level', 'is_verified', 'is_complete', 'sex']
    search_fields = [
        'student_id', 'user__first_name', 'user__last_name',
        'user__email', 'contact_number'
    ]
    readonly_fields = ['created_at', 'updated_at', 'get_age', 'get_bmi']
    
    fieldsets = (
        ('User Account', {
            'fields': ('user',)
        }),
        ('Academic Information', {
            'fields': ('student_id', 'program', 'year_level')
        }),
        ('Personal Information', {
            'fields': (
                'sex', 'date_of_birth', 'contact_number', 'address'
            )
        }),
        ('Emergency Contact', {
            'fields': (
                'emergency_contact_name', 'emergency_contact_relationship',
                'emergency_contact_number', 'emergency_contact_address'
            )
        }),
        ('Medical Information', {
            'fields': (
                'height_cm', 'weight_kg', 'blood_type',
                'allergies', 'current_medications',
                'immunization_history', 'medical_history'
            )
        }),
        ('Dental Information', {
            'fields': (
                'last_dental_visit', 'oral_habits', 'dental_history'
            )
        }),
        ('Status', {
            'fields': ('is_complete', 'is_verified')
        }),
        ('Computed Fields', {
            'fields': ('get_age', 'get_bmi')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def get_full_name(self, obj):
        """Display student's full name."""
        return obj.user.get_full_name()
    get_full_name.short_description = 'Full Name'
    
    def get_age(self, obj):
        """Display student's age."""
        return f"{obj.get_age()} years old"
    get_age.short_description = 'Age'
    
    def get_bmi(self, obj):
        """Display student's BMI."""
        bmi = obj.get_bmi()
        if bmi:
            return f"{bmi:.2f}"
        return "N/A"
    get_bmi.short_description = 'BMI'


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    """Admin for MedicalRecord model."""
    
    list_display = [
        'get_student_id', 'get_student_name', 'record_type',
        'visit_date', 'diagnosis', 'status', 'doctor', 'created_at'
    ]
    list_filter = ['record_type', 'status', 'visit_date', 'created_at']
    search_fields = [
        'student__student_id', 'student__user__first_name',
        'student__user__last_name', 'diagnosis', 'chief_complaint'
    ]
    readonly_fields = ['id', 'created_at', 'updated_at', 'approved_at']
    date_hierarchy = 'visit_date'
    
    fieldsets = (
        ('Record Information', {
            'fields': ('id', 'student', 'doctor', 'record_type', 'visit_date')
        }),
        ('Medical Details', {
            'fields': (
                'chief_complaint', 'diagnosis', 'procedure',
                'prescription', 'remarks'
            )
        }),
        ('Vital Signs', {
            'fields': (
                'blood_pressure', 'temperature',
                'pulse_rate', 'respiratory_rate'
            )
        }),
        ('Attachments', {
            'fields': ('lab_results', 'xray_image', 'attachments')
        }),
        ('Approval Status', {
            'fields': ('status', 'approved_by', 'approved_at')
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
    
    actions = ['approve_records', 'decline_records']
    
    def approve_records(self, request, queryset):
        """Bulk approve selected records."""
        count = 0
        for record in queryset:
            if record.status == 'pending':
                record.approve(request.user)
                count += 1
        
        self.message_user(request, f'{count} record(s) approved successfully.')
    approve_records.short_description = 'Approve selected records'
    
    def decline_records(self, request, queryset):
        """Bulk decline selected records."""
        count = queryset.filter(status='pending').update(status='declined')
        self.message_user(request, f'{count} record(s) declined.')
    decline_records.short_description = 'Decline selected records'


@admin.register(RecordUpdateRequest)
class RecordUpdateRequestAdmin(admin.ModelAdmin):
    """Admin for RecordUpdateRequest model."""
    
    list_display = [
        'get_student_id', 'get_student_name', 'field_name',
        'status', 'created_at', 'expiry_date', 'is_expired_display'
    ]
    list_filter = ['status', 'field_name', 'created_at']
    search_fields = [
        'student__student_id', 'student__user__first_name',
        'student__user__last_name', 'field_name'
    ]
    readonly_fields = ['id', 'created_at', 'expiry_date', 'reviewed_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Request Information', {
            'fields': ('id', 'student', 'field_name')
        }),
        ('Requested Changes', {
            'fields': ('old_value', 'new_value', 'reason', 'supporting_document')
        }),
        ('Review Status', {
            'fields': (
                'status', 'reviewed_by', 'review_notes', 'reviewed_at'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'expiry_date')
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
    
    def is_expired_display(self, obj):
        """Display if request is expired."""
        if obj.is_expired():
            return format_html('<span style="color: red;">✗ Expired</span>')
        return format_html('<span style="color: green;">✓ Active</span>')
    is_expired_display.short_description = 'Status'
    
    actions = ['approve_requests', 'decline_requests', 'mark_expired']
    
    def approve_requests(self, request, queryset):
        """Bulk approve selected requests."""
        count = 0
        for req in queryset:
            if req.status == 'pending':
                req.approve(request.user, apply_changes=True)
                count += 1
        
        self.message_user(request, f'{count} request(s) approved and applied.')
    approve_requests.short_description = 'Approve and apply selected requests'
    
    def decline_requests(self, request, queryset):
        """Bulk decline selected requests."""
        count = 0
        for req in queryset:
            if req.status == 'pending':
                req.decline(request.user, notes='Declined by admin')
                count += 1
        
        self.message_user(request, f'{count} request(s) declined.')
    decline_requests.short_description = 'Decline selected requests'
    
    def mark_expired(self, request, queryset):
        """Mark pending requests as expired if past expiry date."""
        count = 0
        for req in queryset:
            if req.check_and_mark_expired():
                count += 1
        
        self.message_user(request, f'{count} request(s) marked as expired.')
    mark_expired.short_description = 'Mark expired requests'