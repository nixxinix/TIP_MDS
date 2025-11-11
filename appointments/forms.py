"""
Forms for appointment booking and management.
"""

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Appointment, AppointmentNote


class AppointmentBookingForm(forms.ModelForm):
    """
    Form for students to book new appointments.
    """
    
    class Meta:
        model = Appointment
        fields = [
            'service_type', 'preferred_date', 'preferred_time_slot',
            'reason', 'emergency_contact_name', 'emergency_contact_number'
        ]
        widgets = {
            'service_type': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'preferred_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'min': timezone.now().date().isoformat(),
                'required': True
            }),
            'preferred_time_slot': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Briefly describe your concern or reason for appointment',
                'required': True
            }),
            'emergency_contact_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Full name',
                'required': True
            }),
            'emergency_contact_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+63 XXX XXX XXXX',
                'required': True
            }),
        }
    
    def clean_preferred_date(self):
        """Validate that preferred date is in the future."""
        date = self.cleaned_data.get('preferred_date')
        
        if date and date < timezone.now().date():
            raise ValidationError('Please select a future date.')
        
        # Check if date is a weekend (optional - adjust based on clinic schedule)
        if date and date.weekday() >= 5:  # Saturday = 5, Sunday = 6
            raise ValidationError('Appointments are not available on weekends. Please select a weekday.')
        
        return date
    
    def clean_reason(self):
        """Validate reason is not too short."""
        reason = self.cleaned_data.get('reason')
        
        if reason and len(reason.strip()) < 10:
            raise ValidationError('Please provide more details about your reason for appointment.')
        
        return reason


class AppointmentApprovalForm(forms.ModelForm):
    """
    Form for doctors to approve and schedule appointments.
    """
    
    class Meta:
        model = Appointment
        fields = ['doctor', 'actual_datetime', 'doctor_notes']
        widgets = {
            'doctor': forms.Select(attrs={
                'class': 'form-control'
            }),
            'actual_datetime': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'doctor_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Instructions for the patient'
            }),
        }
    
    def clean_actual_datetime(self):
        """Validate scheduled datetime is in the future."""
        dt = self.cleaned_data.get('actual_datetime')
        
        if dt and dt < timezone.now():
            raise ValidationError('Scheduled time must be in the future.')
        
        return dt


class AppointmentRescheduleForm(forms.ModelForm):
    """
    Form to reschedule an appointment.
    """
    
    class Meta:
        model = Appointment
        fields = ['preferred_date', 'preferred_time_slot', 'actual_datetime']
        widgets = {
            'preferred_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'min': timezone.now().date().isoformat()
            }),
            'preferred_time_slot': forms.Select(attrs={
                'class': 'form-control'
            }),
            'actual_datetime': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
        }


class AppointmentCancellationForm(forms.Form):
    """
    Form for cancelling appointments.
    """
    
    cancellation_reason = forms.CharField(
        label='Reason for Cancellation',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Please provide a reason for cancellation',
            'required': True
        })
    )
    
    confirm_cancellation = forms.BooleanField(
        label='I confirm that I want to cancel this appointment',
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )


class AppointmentNoteForm(forms.ModelForm):
    """
    Form for adding notes to appointments.
    """
    
    class Meta:
        model = AppointmentNote
        fields = ['note', 'is_internal']
        widgets = {
            'note': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Add a note or comment...'
            }),
            'is_internal': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class AppointmentSearchForm(forms.Form):
    """
    Form for searching appointments.
    """
    
    search_query = forms.CharField(
        label='Search',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by ticket number, student ID, or name'
        })
    )
    
    service_type = forms.ChoiceField(
        label='Service Type',
        required=False,
        choices=[('', 'All Services')] + list(Appointment.SERVICE_TYPE_CHOICES),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    status = forms.ChoiceField(
        label='Status',
        required=False,
        choices=[('', 'All Status')] + list(Appointment.STATUS_CHOICES),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    date_from = forms.DateField(
        label='Date From',
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    date_to = forms.DateField(
        label='Date To',
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )