"""
Forms for student registration and profile updates.
"""

from django import forms
from django.core.exceptions import ValidationError
from .models import StudentProfile, RecordUpdateRequest
from .models import MedicalRecord

class StudentRegistrationForm(forms.ModelForm):
    """
    Form for new student registration.
    Collects all required information for StudentProfile.
    """
    
    class Meta:
        model = StudentProfile
        fields = [
            'student_id', 'program', 'year_level',
            'sex', 'date_of_birth', 'contact_number', 'address',
            'emergency_contact_name', 'emergency_contact_relationship',
            'emergency_contact_number', 'emergency_contact_address',
            'height_cm', 'weight_kg', 'blood_type',
            'allergies', 'current_medications', 'immunization_history',
            'medical_history', 'last_dental_visit', 'oral_habits',
            'dental_history'
        ]
        widgets = {
            'student_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 2310346'
            }),
            'program': forms.Select(attrs={'class': 'form-control'}),
            'year_level': forms.Select(attrs={'class': 'form-control'}),
            'sex': forms.Select(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'contact_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+63 912 345 6789'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Complete address'
            }),
            'emergency_contact_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Full name'
            }),
            'emergency_contact_relationship': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Parent, Guardian'
            }),
            'emergency_contact_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+63 XXX XXX XXXX'
            }),
            'emergency_contact_address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2
            }),
            'height_cm': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 170.5',
                'step': '0.1'
            }),
            'weight_kg': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 65.0',
                'step': '0.1'
            }),
            'blood_type': forms.Select(attrs={'class': 'form-control'}),
            'allergies': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'List any known allergies'
            }),
            'current_medications': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'List current medications'
            }),
            'immunization_history': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'List vaccines received'
            }),
            'medical_history': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Previous conditions, surgeries, etc.'
            }),
            'last_dental_visit': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'oral_habits': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Teeth grinding, smoking'
            }),
            'dental_history': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Previous dental procedures, concerns'
            }),
        }
    
    def clean_student_id(self):
        """Validate student ID format and uniqueness."""
        student_id = self.cleaned_data.get('student_id')
        
        if not student_id:
            raise ValidationError('Student ID is required.')
        
        # Check if already exists
        if StudentProfile.objects.filter(student_id=student_id).exists():
            raise ValidationError('This student ID is already registered.')
        
        return student_id
    
    def clean_date_of_birth(self):
        """Validate date of birth is in the past."""
        from django.utils import timezone
        dob = self.cleaned_data.get('date_of_birth')
        
        if dob and dob >= timezone.now().date():
            raise ValidationError('Date of birth must be in the past.')
        
        return dob


class StudentUpdateForm(forms.ModelForm):
    """
    Form for students to update their own information.
    Only allows updating certain fields.
    """
    
    class Meta:
        model = StudentProfile
        fields = [
            'contact_number', 'address',
            'emergency_contact_name', 'emergency_contact_relationship',
            'emergency_contact_number', 'emergency_contact_address',
            'height_cm', 'weight_kg',
            'allergies', 'current_medications',
            'oral_habits'
        ]
        widgets = {
            'contact_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'emergency_contact_name': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact_relationship': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact_number': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'height_cm': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'weight_kg': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'allergies': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'current_medications': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'oral_habits': forms.TextInput(attrs={'class': 'form-control'}),
        }


class RecordUpdateRequestForm(forms.ModelForm):
    """
    Form for students to request updates to their medical/dental records.
    Creates a pending request for doctor approval.
    """
    
    class Meta:
        model = RecordUpdateRequest
        fields = ['field_name', 'new_value', 'reason', 'supporting_document']
        widgets = {
            'field_name': forms.Select(attrs={'class': 'form-control'}),
            'new_value': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter new value'
            }),
            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Explain why this update is needed'
            }),
            'supporting_document': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.student_profile = kwargs.pop('student_profile', None)
        super().__init__(*args, **kwargs)
        
        # Customize field choices based on what can be updated
        self.fields['field_name'].choices = [
            ('', '-- Select Field --'),
            ('contact_number', 'Contact Number'),
            ('address', 'Address'),
            ('emergency_contact_name', 'Emergency Contact Name'),
            ('emergency_contact_number', 'Emergency Contact Number'),
            ('height_cm', 'Height'),
            ('weight_kg', 'Weight'),
            ('allergies', 'Allergies'),
            ('current_medications', 'Current Medications'),
            ('medical_history', 'Medical History'),
            ('dental_history', 'Dental History'),
        ]
    
    def clean(self):
        """Store old value before creating request."""
        cleaned_data = super().clean()
        field_name = cleaned_data.get('field_name')
        
        if field_name and self.student_profile:
            old_value = getattr(self.student_profile, field_name, '')
            self.instance.old_value = str(old_value) if old_value else ''
        
        return cleaned_data


class MedicalRecordForm(forms.ModelForm):
    """
    Form for doctors to create medical/dental records.
    """
    
    class Meta:
        model = MedicalRecord
        fields = [
            'record_type', 'visit_date', 'chief_complaint',
            'diagnosis', 'procedure', 'prescription', 'remarks',
            'blood_pressure', 'temperature', 'pulse_rate', 'respiratory_rate',
            'lab_results', 'xray_image', 'attachments'
        ]
        widgets = {
            'record_type': forms.Select(attrs={'class': 'form-control'}),
            'visit_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'chief_complaint': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Main reason for visit'
            }),
            'diagnosis': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Diagnosis or findings'
            }),
            'procedure': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Procedures performed'
            }),
            'prescription': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Medications prescribed'
            }),
            'remarks': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Additional notes'
            }),
            'blood_pressure': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 120/80'
            }),
            'temperature': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 36.5',
                'step': '0.1'
            }),
            'pulse_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'bpm'
            }),
            'respiratory_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'breaths/min'
            }),
            'lab_results': forms.FileInput(attrs={'class': 'form-control'}),
            'xray_image': forms.FileInput(attrs={'class': 'form-control'}),
            'attachments': forms.FileInput(attrs={'class': 'form-control'}),
        }