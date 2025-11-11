"""
Authentication forms for user registration and login.
"""

from django import forms
from doctors.models import DoctorProfile
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from django.conf import settings
from .models import User, UserProfile


class UserRegistrationForm(UserCreationForm):
    """
    Custom registration form with institutional email validation.
    Only allows @tip.edu.ph email addresses.
    MODIFIED: Student-only registration (role field hidden and auto-set)
    """
    
    email = forms.EmailField(
        label='Email Address',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your.name@tip.edu.ph',
            'autocomplete': 'email'
        }),
        help_text='Must be a valid @tip.edu.ph email address'
    )
    
    first_name = forms.CharField(
        label='First Name',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter first name',
            'autocomplete': 'given-name'
        })
    )
    
    last_name = forms.CharField(
        label='Last Name',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter last name',
            'autocomplete': 'family-name'
        })
    )
    
    phone_number = forms.CharField(
        label='Phone Number',
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+63 912 345 6789',
            'autocomplete': 'tel'
        })
    )
    
    # MODIFIED: Role field is now hidden and defaults to 'student'
    role = forms.ChoiceField(
        label='I am a',
        choices=[('student', 'Student'), ('doctor', 'Doctor/Staff')],
        widget=forms.HiddenInput(),  # Hidden input
        initial='student',  # Default to student
        required=False  # Not required in form validation
    )
    
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Create a strong password',
            'autocomplete': 'new-password'
        }),
        help_text='Password must be at least 8 characters'
    )
    
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm your password',
            'autocomplete': 'new-password'
        })
    )
    
    terms_accepted = forms.BooleanField(
        label='I agree to the Terms of Service and Privacy Policy',
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'phone_number', 'role', 'password1', 'password2']
    
    def clean_email(self):
        """Validate that email is from institutional domain."""
        email = self.cleaned_data.get('email')
        
        if not email:
            raise ValidationError('Email is required.')
        
        # Check institutional domain
        institutional_domain = settings.INSTITUTIONAL_EMAIL_DOMAIN
        if not email.endswith(f'@{institutional_domain}'):
            raise ValidationError(
                f'Only {institutional_domain} email addresses are allowed. '
                f'Please use your institutional email.'
            )
        
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            raise ValidationError('This email address is already registered.')
        
        return email.lower()
    
    def clean_phone_number(self):
        """Validate phone number format."""
        phone = self.cleaned_data.get('phone_number')
        if phone:
            # Remove spaces and dashes
            phone = phone.replace(' ', '').replace('-', '')
            # Basic validation
            if not phone.startswith('+') and not phone.isdigit():
                raise ValidationError('Invalid phone number format.')
        return phone
    
    def clean_role(self):
        """Force role to be 'student' for student-only registration."""
        return 'student'
    
    def save(self, commit=True):
        """Save user and create associated profile. Force role to student."""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email'].lower()
        user.role = 'student'  # Force student role
        
        if commit:
            user.save()
            # Use get_or_create to avoid duplicate profile creation
            UserProfile.objects.get_or_create(user=user)
        
        return user


class UserLoginForm(AuthenticationForm):
    """
    Custom login form using email instead of username.
    """
    
    username = forms.EmailField(
        label='Email Address',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your.name@tip.edu.ph',
            'autocomplete': 'email',
            'autofocus': True
        })
    )
    
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password',
            'autocomplete': 'current-password'
        })
    )
    
    remember_me = forms.BooleanField(
        label='Remember me',
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    error_messages = {
        'invalid_login': (
            "Please enter a correct email and password. Note that both "
            "fields may be case-sensitive."
        ),
        'inactive': "This account is inactive.",
    }


class UserProfileForm(forms.ModelForm):
    """Form for updating user profile information."""
    
    first_name = forms.CharField(
        label='First Name',
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    last_name = forms.CharField(
        label='Last Name',
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    phone_number = forms.CharField(
        label='Phone Number',
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    address = forms.CharField(
        label='Address',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3
        })
    )
    
    date_of_birth = forms.DateField(
        label='Date of Birth',
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    emergency_contact_name = forms.CharField(
        label='Emergency Contact Name',
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    emergency_contact_number = forms.CharField(
        label='Emergency Contact Number',
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    emergency_contact_relationship = forms.CharField(
        label='Relationship',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = UserProfile
        fields = [
            'address', 'date_of_birth',
            'emergency_contact_name', 'emergency_contact_number',
            'emergency_contact_relationship'
        ]
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Add user fields
        if self.user:
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name
            self.fields['phone_number'].initial = self.user.phone_number
    
    def save(self, commit=True):
        """Save both user and profile information."""
        profile = super().save(commit=False)
        
        if self.user:
            self.user.first_name = self.cleaned_data['first_name']
            self.user.last_name = self.cleaned_data['last_name']
            self.user.phone_number = self.cleaned_data.get('phone_number')
            
            if commit:
                self.user.save()
                profile.save()
        
        return profile


class PasswordResetRequestForm(forms.Form):
    """Form for requesting password reset."""
    
    email = forms.EmailField(
        label='Email Address',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your.name@tip.edu.ph'
        })
    )
    
    def clean_email(self):
        """Validate email exists in system."""
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email=email).exists():
            raise ValidationError('No account found with this email address.')
        return email.lower()

class DoctorRegistrationForm(forms.ModelForm):
    """
    Form for admin to add new Doctor accounts.
    Admin-only functionality - auto-generates secure password.
    """
    
    email = forms.EmailField(
        label='Email Address',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'doctor.name@tip.edu.ph'
        }),
        help_text='Must be a valid @tip.edu.ph email address'
    )
    
    first_name = forms.CharField(
        label='First Name',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter first name'
        })
    )
    
    last_name = forms.CharField(
        label='Last Name',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter last name'
        })
    )
    
    phone_number = forms.CharField(
        label='Phone Number',
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+63 912 345 6789'
        })
    )
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'phone_number']
    
    def clean_email(self):
        """Validate that email is from institutional domain."""
        email = self.cleaned_data.get('email')
        
        if not email:
            raise ValidationError('Email is required.')
        
        # Check institutional domain
        institutional_domain = settings.INSTITUTIONAL_EMAIL_DOMAIN
        if not email.endswith(f'@{institutional_domain}'):
            raise ValidationError(
                f'Only {institutional_domain} email addresses are allowed.'
            )
        
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            raise ValidationError('This email address is already registered.')
        
        return email.lower()
    
    def save(self, commit=True):
        """Create doctor user with auto-generated password."""
        import random
        import string
        
        user = super().save(commit=False)
        user.email = self.cleaned_data['email'].lower()
        user.role = 'doctor'  # Force doctor role
        
        # Generate secure random password
        temp_password = ''.join(
            random.choices(string.ascii_letters + string.digits + '!@#$%', k=12)
        )
        user.set_password(temp_password)  # Hash password
        
        if commit:
            user.save()
            # Create user profile
            from accounts.models import UserProfile
            UserProfile.objects.get_or_create(user=user)
            
            # Create doctor profile with temp password
            from doctors.models import DoctorProfile
            doctor_profile, created = DoctorProfile.objects.get_or_create(
                user=user,
                defaults={
                    'profile_completed': False,
                    'temp_password': temp_password  # Store for one-time display
                }
            )
            
            # Store temp password in user object for template display
            user.temp_password = temp_password
        
        return user


class DoctorProfileForm(forms.ModelForm):
    """Form for doctor to complete their profile on first login."""
    
    specialization = forms.ChoiceField(
        label='Specialization',
        choices=[('', '--- Select Specialization ---')] + list(DoctorProfile.SPECIALIZATION_CHOICES),
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        required=True
    )
    
    license_number = forms.CharField(
        label='License Number',
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'PRC-123456'
        }),
        help_text='Your Professional Regulation Commission (PRC) license number',
        required=True
    )
    
    class Meta:
        from doctors.models import DoctorProfile
        model = DoctorProfile
        fields = ['specialization', 'license_number']
    
    def clean_license_number(self):
        """Validate license number is unique."""
        license_number = self.cleaned_data.get('license_number')
        
        # Check if license number already exists (excluding current user)
        from doctors.models import DoctorProfile
        existing = DoctorProfile.objects.filter(
            license_number=license_number
        ).exclude(user=self.instance.user if self.instance.pk else None)
        
        if existing.exists():
            raise ValidationError('This license number is already registered.')
        
        return license_number