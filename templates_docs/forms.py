"""
Forms for certificate generation and template management.
"""

from django import forms
from django.core.exceptions import ValidationError
from .models import Template, IssuedCertificate, Prescription


class TemplateForm(forms.ModelForm):
    """
    Form for creating and editing document templates.
    """
    
    class Meta:
        model = Template
        fields = [
            'name', 'template_type', 'description',
            'template_html', 'template_css',
            'header_image', 'footer_text',
            'is_active', 'is_default'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Template name'
            }),
            'template_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2
            }),
            'template_html': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 15,
                'placeholder': 'HTML content with {{variables}}'
            }),
            'template_css': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': 'CSS styles (optional)'
            }),
            'header_image': forms.FileInput(attrs={'class': 'form-control'}),
            'footer_text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class CertificateGenerationForm(forms.ModelForm):
    """
    Form for generating certificates for students.
    """
    
    student_id = forms.CharField(
        label='Student ID',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 2310346'
        })
    )
    
    class Meta:
        model = IssuedCertificate
        fields = [
            'title', 'purpose', 'diagnosis',
            'prescription', 'remarks',
            'date_issued', 'valid_until', 'template'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Medical Certificate'
            }),
            'purpose': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Purpose of certificate'
            }),
            'diagnosis': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Diagnosis or findings'
            }),
            'prescription': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Medications prescribed'
            }),
            'remarks': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional remarks'
            }),
            'date_issued': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'valid_until': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'template': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter active templates only
        self.fields['template'].queryset = Template.objects.filter(is_active=True)


class PrescriptionForm(forms.ModelForm):
    """
    Form for creating electronic prescriptions.
    """
    
    student_id = forms.CharField(
        label='Student ID',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 2310346'
        })
    )
    
    class Meta:
        model = Prescription
        fields = [
            'diagnosis', 'medications', 'instructions',
            'date_issued', 'valid_until'
        ]
        widgets = {
            'diagnosis': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Diagnosis or condition'
            }),
            'medications': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'List medications with dosage and frequency\nExample:\n1. Amoxicillin 500mg - 1 capsule 3x a day - 7 days\n2. Paracetamol 500mg - 1 tablet every 4-6 hours as needed for pain'
            }),
            'instructions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Special instructions for the patient'
            }),
            'date_issued': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'valid_until': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }


class CertificateSearchForm(forms.Form):
    """
    Form for searching certificates.
    """
    
    search_query = forms.CharField(
        label='Search',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by certificate number, student ID, or name'
        })
    )
    
    status = forms.ChoiceField(
        label='Status',
        required=False,
        choices=[('', 'All Status')] + list(IssuedCertificate.STATUS_CHOICES),
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